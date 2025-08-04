import torch
import pandas as pd
import numpy as np
import torch.nn.functional as F

# 设备配置
from torch import nn

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 定义特征字段（78 个字段）
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

# 定义 LSTM 模型（与训练时一致）
class LSTM_Model(nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=2, num_classes=8):
        super(LSTM_Model, self).__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True
        )
        self.dropout = nn.Dropout(0.3)
        self.fc1 = nn.Linear(hidden_size, 128)
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = x.unsqueeze(1)  # (batch_size, 1, input_size)
        lstm_out, (hn, cn) = self.lstm(x)
        x = lstm_out[:, -1, :]
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

# 加载均值和标准差
def load_stats(means_path="./mean_std/means.txt", stds_path="./mean_std/stds.txt"):
    means = {}
    stds = {}
    with open(means_path, 'r', encoding='utf-8') as f:
        for line in f:
            col, value = line.strip().split(': ')
            means[col] = float(value)
    with open(stds_path, 'r', encoding='utf-8') as f:
        for line in f:
            col, value = line.strip().split(': ')
            stds[col] = float(value)
    return means, stds

# 加载类别名称（新格式：每行一个类别名称）
def load_class_names(class_names_path="./mean_std/class_names.txt"):
    class_names = []
    with open(class_names_path, 'r', encoding='utf-8') as f:
        for line in f:
            name = line.strip()  # 直接读取类别名称
            if name:  # 忽略空行
                class_names.append(name)
    return class_names

# 预处理单条数据
def preprocess_single_data(data, means, stds, feature_columns):
    data_df = pd.DataFrame([data], columns=feature_columns)
    if data_df.isna().any().any() or np.isinf(data_df.values).any():
        print("警告：输入数据中存在 NaN 或 inf，正在处理...")
        data_df = data_df.replace([np.inf, -np.inf], np.nan).fillna(0)
    means_series = pd.Series(means)
    stds_series = pd.Series(stds)
    data_normalized = (data_df - means_series) / stds_series
    data_normalized = data_normalized.fillna(0)
    data_tensor = torch.tensor(data_normalized.values, dtype=torch.float32).to(device)
    return data_tensor

# 测试单条数据
def test_single_data(model, data_tensor, class_names):
    model.eval()
    with torch.no_grad():
        output = model(data_tensor)
        probs = F.softmax(output, dim=1).cpu().numpy()[0]
        pred_class_idx = torch.argmax(output, dim=1).cpu().numpy()[0]
        pred_class = class_names[pred_class_idx]
    return pred_class, probs

if __name__ == "__main__":
    # 参数配置
    input_size = len(feature_columns)  # 78
    num_classes = 8
    hidden_size = 64
    num_layers = 2
    model_path = "model/best_model_lstm.pth"
    means_path = "./mean_std/means.txt"
    stds_path = "./mean_std/stds.txt"
    class_names_path = "./mean_std/class_names.txt"

    # 加载类别名称
    class_names = load_class_names(class_names_path)
    print("类别名称已加载:", class_names)

    # 验证类别数量
    if len(class_names) != num_classes:
        raise ValueError(f"类别数量不匹配：文件中找到 {len(class_names)} 个类别，模型期望 {num_classes} 个")

    # 加载模型
    model = LSTM_Model(
        input_size=input_size,
        hidden_size=hidden_size,
        num_layers=num_layers,
        num_classes=num_classes
    )
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    print("模型已加载")

    # 加载均值和标准差
    means, stds = load_stats(means_path, stds_path)
    print("均值和标准差已加载")

    sample_data = [
        80, 92.98324584960938, 1, 1, 74, 66, 74.0, 74.0, 74.0, 0.0, 66.0, 66.0, 66.0, 0.0, 1505647.5897435895,
        21509.25128205128, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0, 0, 0, 52,
        10754.62564102564, 10754.62564102564, 66.0, 74.0, 70.0, 4.0, 16.0, 0, 2, 0, 0, 1, 0, 0, 0, 1.121212121212121,
        70.0, 74.0, 66.0, 0, 0, 0, 0, 0, 0, 0, 1, 74, 1, 66, 0, 65535, 0, 0, 9.298324584960938e-05, 0.0,
        9.298324584960938e-05, 9.298324584960938e-05, 0.0, 0.0, 0.0, 0.0
    ]
    # 或者从 CSV 读取
    # test_df = pd.read_csv("single_sample.csv")
    # sample_data = test_df[feature_columns].iloc[0].values.tolist()

    # 预处理单条数据
    data_tensor = preprocess_single_data(sample_data, means, stds, feature_columns)

    # 测试单条数据
    pred_class, probs = test_single_data(model, data_tensor, class_names)

    # 输出结果
    print("\n预测结果：")
    print(f"预测类别: {pred_class}")
    print("各类别概率：")
    for cls, prob in zip(class_names, probs):
        print(f"{cls}: {prob:.4f}")