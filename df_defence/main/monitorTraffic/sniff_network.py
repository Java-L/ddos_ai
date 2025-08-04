# 作者: 小牛667
# 创建时间: 2025-04-12

import pandas as pd
import torch
from scapy.all import *
from scapy.layers.inet import IP, TCP, UDP
from torch import nn
from scapy.all import sniff, IP, TCP, UDP, ICMP, get_if_list, get_if_addr
from collections import defaultdict
import numpy as np
from main import config
from main.DL.cnn.test import CNN_Model
from main.DL.cnn_lstm_attention.test import CNN_LSTM_Attention_Model
from main.DL.lstm.test import load_class_names, LSTM_Model, device, load_stats, preprocess_single_data, test_single_data
from main.config import ATTACK_MAPPING, THREAT_MAPPING
import logging

# 配置日志记录，方便调试和错误追踪
from main.sql.sqlquery import SQLFather

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

flows = defaultdict(lambda: {
    'start_time': None,
    'packets': [],
    'in_bytes': 0,
    'out_bytes': 0,
    'in_pkts': [],
    'out_pkts': [],
    'in_iat': [],
    'out_iat': [],
    'last_in_ts': None,
    'last_out_ts': None,
    'in_flags': {'FIN': 0, 'PSH': 0, 'ACK': 0, 'URG': 0, 'SYN': 0, 'RST': 0},
    'out_flags': {'FIN': 0, 'PSH': 0, 'ACK': 0, 'URG': 0, 'SYN': 0, 'RST': 0},
    'init_out_win': None,
    'in_act_data_pkts': 0,
    'active_times': [],
    'idle_times': [],
    'last_packet_ts': None
})

feature_columns = [
    "Destination Port", "Flow Duration", "Total Fwd Packets", "Total Backward Packets",
    "Total Length of Fwd Packets", "Total Length of Bwd Packets", "Fwd Packet Length Max",
    "Fwd Packet Length Min", "Fwd Packet Length Mean", "Fwd Packet Length Std",
    "Bwd Packet Length Max", "Bwd Packet Length Min", "Bwd Packet Length Mean",
    "Bwd Packet Length Std", "Flow Bytes/s", "Flow Packets/s", "Flow IAT Mean",
    "Flow IAT Std", "Flow IAT Max", "Flow IAT Min", "Fwd IAT Total", "Fwd IAT Mean",
    "Fwd IAT Std", "Fwd IAT Max", "Fwd IAT Min", "Bwd IAT Total", "Bwd IAT Mean",
    "Bwd IAT Std", "Bwd IAT Max", "Bwd IAT Min", "Fwd PSH Flags", "Bwd PSH Flags",
    "Fwd URG Flags", "Bwd URG Flags", "Fwd Header Length", "Bwd Header Length",
    "Fwd Packets/s", "Bwd Packets/s", "Min Packet Length", "Max Packet Length",
    "Packet Length Mean", "Packet Length Std", "Packet Length Variance", "FIN Flag Count",
    "SYN Flag Count", "RST Flag Count", "PSH Flag Count", "ACK Flag Count", "URG Flag Count",
    "CWE Flag Count", "ECE Flag Count", "Down/Up Ratio", "Average Packet Size",
    "Avg Fwd Segment Size", "Avg Bwd Segment Size", "Fwd Header Length.1",
    "Fwd Avg Bytes/Bulk", "Fwd Avg Packets/Bulk", "Fwd Avg Bulk Rate",
    "Bwd Avg Bytes/Bulk", "Bwd Avg Packets/Bulk", "Bwd Avg Bulk Rate",
    "Subflow Fwd Packets", "Subflow Fwd Bytes", "Subflow Bwd Packets",
    "Subflow Bwd Bytes", "Init_Win_bytes_forward", "Init_Win_bytes_backward",
    "act_data_pkt_fwd", "min_seg_size_forward", "Active Mean", "Active Std",
    "Active Max", "Active Min", "Idle Mean", "Idle Std", "Idle Max", "Idle Min"
]


# 获取本机 IP 地址
def get_local_ip(iface):
    try:
        return get_if_addr(iface)
    except Exception as e:
        print(f"无法获取网卡 {iface} 的 IP 地址: {e}")
        return None


class NetworkSniffer:
    def __init__(self, interface, port, model_type="lstm"):
        # 参数配置
        input_size = 78
        num_classes = 8
        hidden_size = 64
        num_layers = 2
        # 动态选择模型路径
        model_paths = {
            "lstm": os.path.join(config.MODELS_DIRS, "best_model_lstm.pth"),
            "cnn": os.path.join(config.MODELS_DIRS, "best_model_cnn.pth"),
            "cnn_lstm_attention": os.path.join(config.MODELS_DIRS, "best_model_cnn_lstm_attention.pth")
        }
        # 确保选择的模型类型有效
        if model_type not in model_paths:
            raise ValueError(f"不支持的模型类型: {model_type}. 可选类型: {list(model_paths.keys())}")

        model_path = model_paths[model_type]
        means_path = config.MEANS_PATH
        stds_path = config.STDS_PATH
        class_names_path = config.CLASS_NAMES_PATH

        # 加载类别名称
        self.class_names = load_class_names(class_names_path)
        print("Class names loaded:", self.class_names)

        # 验证类别数量
        if len(self.class_names) != num_classes:
            raise ValueError(f"类别数量不匹配：文件中找到 {len(self.class_names)} 个类别，模型期望 {num_classes} 个")

        # # 加载模型
        # self.model = LSTM_Model(
        #     input_size=input_size,
        #     hidden_size=hidden_size,
        #     num_layers=num_layers,
        #     num_classes=num_classes
        # )
        # 根据模型类型加载对应模型
        if model_type == "lstm":
            self.model = LSTM_Model(
                input_size=input_size,
                hidden_size=hidden_size,
                num_layers=num_layers,
                num_classes=num_classes
            )
        elif model_type == "cnn":
            self.model = CNN_Model(
                input_size=input_size,
                num_classes=num_classes
            )
        elif model_type == "cnn_lstm_attention":
            self.model = CNN_LSTM_Attention_Model(
                input_size=input_size,
                num_classes=num_classes
            )

        self.model.load_state_dict(torch.load(model_path, map_location=device))
        self.model.to(device)
        self.means, self.stds = load_stats(means_path, stds_path)

        print(model_type + " model loaded")
        self.buffer_lock = threading.Lock()  # 初始化锁

        # 流量相关的
        self.url_buffer = []
        self.traffic_queue = queue.Queue()
        self.running = True
        self.processing_thread = threading.Thread(target=self.process_traffic)
        # 开启异步线程消费队列中的流量数据
        self.processing_thread.start()

        """
        初始化嗅探器
        :param interface: Network interface to monitor, e.g. "eth0" or "Wi-Fi"
        :param port: Port to monitor, e.g. 80
        :param count: 捕获数据包数量，0 表示无限捕获
        """
        self.interface = interface
        self.port = port
        self.local_ip = get_local_ip(interface)

        # 设置过滤规则
        if port is None or port == 0:
            self.filter_rule = "tcp"  # 监听所有 TCP 流量
            print(f"Monitoring interface: {self.interface}, monitoring all ports")
        else:
            self.filter_rule = f"tcp port {self.port}"  # 监听指定端口
            print(f"Monitoring interface: {self.interface}, monitoring port: {self.port}")

    def extract_packet_ip(self, packet):
        if IP in packet:
            ip_layer = packet[IP]
            src_ip = ip_layer.src
            dst_ip = ip_layer.dst
            proto = ip_layer.proto
            if proto == 6:
                tcp_layer = packet[TCP]
                dport = tcp_layer.dport
                sport = tcp_layer.sport
            elif proto == 17:
                udp_layer = packet[UDP]
                dport = udp_layer.dport
                sport = udp_layer.sport
        else:
            src_ip = dst_ip = proto = dport = sport = 'UnKnown'
            print("数据包中不存在IP层，无法识别")

        return src_ip, dst_ip, sport, dport, proto

    def is_attack(self, item):
        data_tensor = preprocess_single_data(item, self.means, self.stds, feature_columns)

        # 测试单条数据
        pred_class, probs = test_single_data(self.model, data_tensor, self.class_names)
        return pred_class

    def process_traffic(self):
        buffer = []
        while self.running:
            try:
                # 从队列获取数据
                packet_data = self.traffic_queue.get(timeout=0.5)
                with self.buffer_lock:  # 加锁
                    buffer.append(packet_data)

                # 实时处理单个数据包
                with self.buffer_lock:  # 加锁
                    item = buffer[0]  # 获取第一条数据
                    features = item['features']  # 提取特征
                    five_tuple = item['five_tuple']  # 提取五元组

                    is_attack = self.is_attack(features)
                    print(f"检测结果: {is_attack}")

                    # 保存数据包到数据库
                    try:
                        self.save_packet(five_tuple, features, is_attack)
                    except Exception as e:
                        logging.error(f"保存数据包到数据库时出错: {e}, 五元组: {five_tuple}, 特征: {features}")

                    buffer.pop(0)  # 移除已处理的项
                    logging.info(f"实时处理 1 条记录，缓冲区剩余 {len(buffer)} 条")

            except queue.Empty:
                with self.buffer_lock:  # 加锁
                    # 队列为空时，处理缓冲区中剩余的数据
                    if buffer:
                        item = buffer[0]
                        features = item['features']
                        five_tuple = item['five_tuple']

                        is_attack = self.is_attack(features)
                        print(f"检测结果: {is_attack}")

                        try:
                            self.save_packet(five_tuple, features, is_attack)
                        except Exception as e:
                            logging.error(f"保存数据包到数据库时出错: {e}, 五元组: {five_tuple}, 特征: {features}")

                        buffer.pop(0)  # 移除已处理的项
                        logging.info(f"实时处理 1 条记录，缓冲区剩余 {len(buffer)} 条")
                    continue
            except Exception as e:
                logging.error(f"处理流量时发生未预期的错误: {e}")
                continue

    def stop(self):
        self.running = False
        self.processing_thread.join()

    def save_packet(self, five_tuple, features, is_attack):
        try:
            attack_type = ATTACK_MAPPING.get(is_attack, '未检测到攻击')
            threat = THREAT_MAPPING.get(attack_type, '未检测到威胁')
            sql_father = SQLFather()

            # 解包五元组
            src_ip, dst_ip, src_port, dst_port, proto = five_tuple
            # 将features转为字符串
            features = str(features)
            # 构造数据字典
            data = {
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "src_port": src_port,
                "dst_port": dst_port,
                "protocol": proto,
                "features": features,
                "attack_type": attack_type,
                "threat": threat,
                "create_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }

            # 打印流量信息
            print("五元组:", five_tuple)
            print("攻击类型:", attack_type)
            print("威胁程度:", threat)

            # 插入数据库
            sql_father.insertPacket(data)
        except Exception as e:
            logging.error(f"保存数据包到数据库时出错: {e}, 五元组: {five_tuple}")

    def extract_features(self, packet, target_port=None, local_ip=None):
        if IP not in packet:
            return None

        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        proto = packet[IP].proto
        src_port = packet.sport if TCP in packet or UDP in packet else 0
        dst_port = packet.dport if TCP in packet or UDP in packet else 0

        # 如果指定了目标端口，过滤不匹配的流量
        if target_port is not None and dst_port != target_port and src_port != target_port:
            return None

        # 使用双向流的键值
        flow_key = tuple(sorted([(src_ip, src_port), (dst_ip, dst_port)]) + [proto])
        flow = flows[flow_key]
        if flow['start_time'] is None:
            flow['start_time'] = packet.time

        # 判断流量方向
        is_incoming = (local_ip is not None and packet[IP].dst == local_ip)
        pkt_len = len(packet)

        if flow['last_packet_ts'] is not None:
            iat = packet.time - flow['last_packet_ts']
            if iat > 1.0:  # 假设 IAT > 1 秒为 Idle
                flow['idle_times'].append(iat)
            else:
                flow['active_times'].append(iat)
        flow['last_packet_ts'] = packet.time

        flow['packets'].append(packet)
        if is_incoming:
            flow['in_bytes'] += pkt_len
            flow['in_pkts'].append(pkt_len)
            if flow['last_in_ts'] is not None:
                iat = packet.time - flow['last_in_ts']
                flow['in_iat'].append(iat)
            flow['last_in_ts'] = packet.time
            if TCP in packet and len(packet[TCP].payload) > 0:
                flow['in_act_data_pkts'] += 1
        else:
            flow['out_bytes'] += pkt_len
            flow['out_pkts'].append(pkt_len)
            if flow['last_out_ts'] is not None:
                iat = packet.time - flow['last_out_ts']
                flow['out_iat'].append(iat)
            flow['last_out_ts'] = packet.time
            if TCP in packet and flow['init_out_win'] is None:
                flow['init_out_win'] = packet[TCP].window

        # TCP Flags 处理
        if TCP in packet:
            flags = packet[TCP].flags
            flag_dict = flow['in_flags'] if is_incoming else flow['out_flags']
            try:
                flag_dict['FIN'] += 1 if flags.FIN else 0
                flag_dict['PSH'] += 1 if flags.PSH else 0
                flag_dict['ACK'] += 1 if flags.ACK else 0
                flag_dict['URG'] += 1 if flags.URG else 0
                flag_dict['SYN'] += 1 if flags.SYN else 0
                flag_dict['RST'] += 1 if flags.RST else 0
            except AttributeError:
                flag_dict['FIN'] += 1 if (flags & 0x01) else 0
                flag_dict['PSH'] += 1 if (flags & 0x08) else 0
                flag_dict['ACK'] += 1 if (flags & 0x10) else 0
                flag_dict['URG'] += 1 if (flags & 0x20) else 0
                flag_dict['SYN'] += 1 if (flags & 0x02) else 0
                flag_dict['RST'] += 1 if (flags & 0x04) else 0

        duration = packet.time - flow['start_time'] if flow['start_time'] else 0
        duration = max(duration, 1e-6)

        total_bytes = flow['in_bytes'] + flow['out_bytes']
        total_pkts = len(flow['in_pkts']) + len(flow['out_pkts'])
        in_pkts = np.array(flow['in_pkts']) if flow['in_pkts'] else np.array([0])
        out_pkts = np.array(flow['out_pkts']) if flow['out_pkts'] else np.array([0])
        all_pkts = np.concatenate([in_pkts, out_pkts]) if total_pkts > 0 else np.array([0])
        in_iat = np.array(flow['in_iat']) if flow['in_iat'] else np.array([0])
        out_iat = np.array(flow['out_iat']) if flow['out_iat'] else np.array([0])
        all_iat = np.concatenate([in_iat, out_iat]) if total_pkts > 1 else np.array([0])
        active_times = np.array(flow['active_times']) if flow['active_times'] else np.array([0])
        idle_times = np.array(flow['idle_times']) if flow['idle_times'] else np.array([0])

        # 按照指定顺序定义特征
        features = {}
        features["Destination Port"] = dst_port if is_incoming else src_port
        features["Flow Duration"] = duration * 1e6
        features["Total Fwd Packets"] = len(flow['in_pkts'])
        features["Total Backward Packets"] = len(flow['out_pkts'])
        features["Total Length of Fwd Packets"] = flow['in_bytes']
        features["Total Length of Bwd Packets"] = flow['out_bytes']
        features["Fwd Packet Length Max"] = float(np.max(in_pkts))
        features["Fwd Packet Length Min"] = float(np.min(in_pkts))
        features["Fwd Packet Length Mean"] = float(np.mean(in_pkts)) if len(in_pkts) > 0 else 0
        features["Fwd Packet Length Std"] = float(np.std(in_pkts)) if len(in_pkts) > 1 else 0
        features["Bwd Packet Length Max"] = float(np.max(out_pkts))
        features["Bwd Packet Length Min"] = float(np.min(out_pkts))
        features["Bwd Packet Length Mean"] = float(np.mean(out_pkts)) if len(out_pkts) > 0 else 0
        features["Bwd Packet Length Std"] = float(np.std(out_pkts)) if len(out_pkts) > 1 else 0
        features["Flow Bytes/s"] = total_bytes / duration if total_pkts > 0 else 0
        features["Flow Packets/s"] = total_pkts / duration if total_pkts > 0 else 0
        features["Flow IAT Mean"] = float(np.mean(all_iat)) if len(all_iat) > 0 else 0
        features["Flow IAT Std"] = float(np.std(all_iat)) if len(all_iat) > 1 else 0
        features["Flow IAT Max"] = float(np.max(all_iat))
        features["Flow IAT Min"] = float(np.min(all_iat))
        features["Fwd IAT Total"] = float(np.sum(in_iat))
        features["Fwd IAT Mean"] = float(np.mean(in_iat)) if len(in_iat) > 0 else 0
        features["Fwd IAT Std"] = float(np.std(in_iat)) if len(in_iat) > 1 else 0
        features["Fwd IAT Max"] = float(np.max(in_iat))
        features["Fwd IAT Min"] = float(np.min(in_iat))
        features["Bwd IAT Total"] = float(np.sum(out_iat))
        features["Bwd IAT Mean"] = float(np.mean(out_iat)) if len(out_iat) > 0 else 0
        features["Bwd IAT Std"] = float(np.std(out_iat)) if len(out_iat) > 1 else 0
        features["Bwd IAT Max"] = float(np.max(out_iat))
        features["Bwd IAT Min"] = float(np.min(out_iat))
        features["Fwd PSH Flags"] = flow['in_flags']['PSH']
        features["Bwd PSH Flags"] = flow['out_flags']['PSH']
        features["Fwd URG Flags"] = flow['in_flags']['URG']
        features["Bwd URG Flags"] = flow['out_flags']['URG']
        features["Fwd Header Length"] = packet[IP].ihl * 4 + packet[
            TCP].dataofs * 4 if TCP in packet and is_incoming else 0
        features["Bwd Header Length"] = packet[IP].ihl * 4 + packet[
            TCP].dataofs * 4 if TCP in packet and not is_incoming else 0
        features["Fwd Packets/s"] = len(flow['in_pkts']) / duration if len(flow['in_pkts']) > 0 else 0
        features["Bwd Packets/s"] = len(flow['out_pkts']) / duration if len(flow['out_pkts']) > 0 else 0
        features["Min Packet Length"] = float(np.min(all_pkts))
        features["Max Packet Length"] = float(np.max(all_pkts))
        features["Packet Length Mean"] = float(np.mean(all_pkts)) if len(all_pkts) > 0 else 0
        features["Packet Length Std"] = float(np.std(all_pkts)) if len(all_pkts) > 1 else 0
        features["Packet Length Variance"] = float(np.var(all_pkts)) if len(all_pkts) > 1 else 0
        features["FIN Flag Count"] = flow['in_flags']['FIN'] + flow['out_flags']['FIN']
        features["SYN Flag Count"] = flow['in_flags']['SYN'] + flow['out_flags']['SYN']
        features["RST Flag Count"] = flow['in_flags']['RST'] + flow['out_flags']['RST']
        features["PSH Flag Count"] = flow['in_flags']['PSH'] + flow['out_flags']['PSH']
        features["ACK Flag Count"] = flow['in_flags']['ACK'] + flow['out_flags']['ACK']
        features["URG Flag Count"] = flow['in_flags']['URG'] + flow['out_flags']['URG']
        features["CWE Flag Count"] = 0  # 未定义，设为 0
        features["ECE Flag Count"] = 0  # 未定义，设为 0
        features["Down/Up Ratio"] = flow['in_bytes'] / flow['out_bytes'] if flow['out_bytes'] > 0 else 0
        features["Average Packet Size"] = (total_bytes / total_pkts) if total_pkts > 0 else 0
        features["Avg Fwd Segment Size"] = float(np.mean(in_pkts)) if len(in_pkts) > 0 else 0
        features["Avg Bwd Segment Size"] = float(np.mean(out_pkts)) if len(out_pkts) > 0 else 0
        features["Fwd Header Length.1"] = features["Fwd Header Length"]  # 假设为重复字段
        features["Fwd Avg Bytes/Bulk"] = 0
        features["Fwd Avg Packets/Bulk"] = 0
        features["Fwd Avg Bulk Rate"] = 0
        features["Bwd Avg Bytes/Bulk"] = 0
        features["Bwd Avg Packets/Bulk"] = 0
        features["Bwd Avg Bulk Rate"] = 0
        features["Subflow Fwd Packets"] = len(flow['in_pkts'])
        features["Subflow Fwd Bytes"] = flow['in_bytes']
        features["Subflow Bwd Packets"] = len(flow['out_pkts'])
        features["Subflow Bwd Bytes"] = flow['out_bytes']
        features["Init_Win_bytes_forward"] = packet[TCP].window if TCP in packet and is_incoming else 0
        features["Init_Win_bytes_backward"] = flow['init_out_win'] if flow['init_out_win'] is not None else 0
        features["act_data_pkt_fwd"] = flow['in_act_data_pkts']
        features["min_seg_size_forward"] = packet[IP].ihl * 4 + packet[
            TCP].dataofs * 4 if TCP in packet and is_incoming else 0
        features["Active Mean"] = float(np.mean(active_times)) if len(active_times) > 0 else 0
        features["Active Std"] = float(np.std(active_times)) if len(active_times) > 1 else 0
        features["Active Max"] = float(np.max(active_times))
        features["Active Min"] = float(np.min(active_times))
        features["Idle Mean"] = float(np.mean(idle_times)) if len(idle_times) > 0 else 0
        features["Idle Std"] = float(np.std(idle_times)) if len(idle_times) > 1 else 0
        features["Idle Max"] = float(np.max(idle_times))
        features["Idle Min"] = float(np.min(idle_times))

        return features

    def packet_callback(self, packet):
        print("正在监听流量数据包.....")
        five_features = self.extract_features(packet, target_port=self.port, local_ip=self.local_ip)
        feats = self.extract_packet_ip(packet)
        if feats and five_features:
            # 将五元组和特征打包为一个字典，放入队列
            packet_data = {
                'five_tuple': feats,  # 五元组: (src_ip, dst_ip, src_port, dst_port, proto)
                'features': five_features  # 提取的特征
            }
            self.traffic_queue.put(packet_data)

    def start_sniffing(self):
        """开始嗅探流量"""
        print(f"Starting to monitor traffic on {self.interface} port {self.port}...")
        try:
            sniff(iface=self.interface, filter=self.filter_rule, prn=self.packet_callback)
        except ValueError as e:
            # 捕获接口不存在的异常
            print(f"错误: {e}")
            print("可用网络接口列表如下，请检查并更新配置：")
            available_interfaces = get_if_list()
            for iface in available_interfaces:
                print(f" - {iface}")
            print("建议：修改 config.INTERFACE 或数据库中的 interface 值")
        except Scapy_Exception as e:
            # 捕获权限不足的异常
            print(f"错误: {e}")
            print("权限不足！请以管理员/root 权限运行程序，例如使用 'sudo python script.py'")
            print("在 macOS 上，可能需要额外的权限调整，例如：")
            print("  sudo chmod o+r /dev/bpf*")
        except Exception as e:
            # 捕获其他未预期的异常
            print(f"Unknown error: {e}")
            print("Please check network environment or contact administrator")
