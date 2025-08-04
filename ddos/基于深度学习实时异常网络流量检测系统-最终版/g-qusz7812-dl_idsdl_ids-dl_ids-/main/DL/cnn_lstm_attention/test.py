import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import pandas as pd

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class Attention(nn.Module):
    def __init__(self, hidden_size):
        super(Attention, self).__init__()
        self.hidden_size = hidden_size
        self.attention = nn.Linear(hidden_size, 1)
        
    def forward(self, lstm_output):
        attention_weights = F.softmax(self.attention(lstm_output), dim=1)
        context = torch.sum(attention_weights * lstm_output, dim=1)
        return context, attention_weights

class CNN_LSTM_Attention_Model(nn.Module):
    def __init__(self, input_size, num_classes=8):
        super(CNN_LSTM_Attention_Model, self).__init__()
        
        # CNN部分
        self.conv1 = nn.Conv1d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool1d(2)
        
        # 计算CNN输出大小
        cnn_output_size = input_size // (2 ** 2)  # 经过2次池化
        
        # LSTM部分
        self.lstm = nn.LSTM(
            input_size=64 * cnn_output_size,
            hidden_size=128,
            num_layers=2,
            batch_first=True,
            bidirectional=True
        )
        
        # 注意力机制
        self.attention = Attention(hidden_size=256)  # 双向LSTM，hidden_size * 2
        
        # 全连接层
        self.dropout = nn.Dropout(0.3)
        self.fc1 = nn.Linear(256, 128)
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        batch_size = x.size(0)
        
        # CNN处理
        x = x.unsqueeze(1)  # (batch_size, 1, input_size)
        x = F.relu(self.conv1(x))
        x = self.pool(x)
        x = F.relu(self.conv2(x))
        x = self.pool(x)
        
        # 重塑为LSTM输入格式
        x = x.view(batch_size, 1, -1)  # (batch_size, 1, 64 * cnn_output_size)
        
        # LSTM处理
        lstm_out, _ = self.lstm(x)  # (batch_size, 1, 256)
        
        # 注意力机制
        context, attention_weights = self.attention(lstm_out)
        
        # 全连接层
        x = F.relu(self.fc1(context))
        x = self.dropout(x)
        x = self.fc2(x)
        
        return x

def load_means_stds(means_path="./mean_std/means.txt", stds_path="./mean_std/stds.txt"):
    means = {}
    stds = {}
    
    with open(means_path, 'r', encoding='utf-8') as f:
        for line in f:
            col, mean = line.strip().split(': ')
            means[col] = float(mean)
            
    with open(stds_path, 'r', encoding='utf-8') as f:
        for line in f:
            col, std = line.strip().split(': ')
            stds[col] = float(std)
            
    return means, stds

def load_class_names(class_names_path="./mean_std/class_names.txt"):
    class_names = []
    with open(class_names_path, 'r', encoding='utf-8') as f:
        for line in f:
            class_names.append(line.strip())
    return class_names

def preprocess_data(data, means, stds):
    # 确保数据是DataFrame格式
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)
    
    # 标准化数据
    for col in data.columns:
        if col in means and col in stds:
            data[col] = (data[col] - means[col]) / stds[col]
    
    # 处理缺失值和无穷值
    data = data.replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # 转换为tensor
    data_tensor = torch.tensor(data.values, dtype=torch.float32)
    return data_tensor

def test_single_instance(model, data, means, stds, class_names):
    # 预处理数据
    data_tensor = preprocess_data(data, means, stds)
    data_tensor = data_tensor.to(device)
    
    # 模型预测
    model.eval()
    with torch.no_grad():
        output = model(data_tensor)
        probabilities = F.softmax(output, dim=1)
        predicted_class = torch.argmax(probabilities, dim=1).item()
        class_probabilities = probabilities[0].cpu().numpy()
    
    # 返回预测结果
    result = {
        'predicted_class': class_names[predicted_class],
        'probabilities': {class_names[i]: float(prob) for i, prob in enumerate(class_probabilities)}
    }
    
    return result

def main():
    # 加载模型
    model_path = "model/best_model_cnn_lstm_attention.pth"
    model = CNN_LSTM_Attention_Model(input_size=78)  # 78是特征数量
    model.load_state_dict(torch.load(model_path))
    model = model.to(device)
    
    # 加载均值和标准差
    means, stds = load_means_stds()
    
    # 加载类别名称
    class_names = load_class_names()
    
    # 示例数据
    sample_data = pd.DataFrame(np.random.randn(1, 78))  # 替换为实际数据
    
    # 测试单个实例
    result = test_single_instance(model, sample_data, means, stds, class_names)
    
    # 打印结果
    print(f"预测类别: {result['predicted_class']}")
    print("各类别概率:")
    for class_name, prob in result['probabilities'].items():
        print(f"{class_name}: {prob:.4f}")

if __name__ == "__main__":
    main() 