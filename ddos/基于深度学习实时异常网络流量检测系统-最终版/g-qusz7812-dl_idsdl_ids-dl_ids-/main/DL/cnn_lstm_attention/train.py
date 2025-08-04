import lime
import lime.lime_tabular
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import numpy as np
import pandas as pd
import seaborn as sns
import shap
import torch
import torch.nn as nn
import torch.nn.functional as F
from pylab import mpl
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import shuffle
from torch.utils.data import TensorDataset, DataLoader
from torch.utils.tensorboard import SummaryWriter

# 设置中文显示字体
mpl.rcParams["font.sans-serif"] = ["SimHei"]
mpl.rcParams["axes.unicode_minus"] = False
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
loss_fn = nn.CrossEntropyLoss().to(device)

# 设置 TensorBoard 日志目录
writer_train = SummaryWriter(r"main/DL/draw/train_Board")
writer_valid = SummaryWriter(r"main/DL/draw/valid_Board")

def count_outcome_categories(df, dataset_name=""):
    outcome_counts = df[' Label'].value_counts()
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(x=outcome_counts.index, y=outcome_counts.values)
    plt.yscale('log')
    plt.title(f'{dataset_name} 数据集 - Outcome 类别分布')
    plt.xlabel('类别')
    plt.ylabel('数量 (对数尺度)')
    plt.xticks(rotation=45, ha='right')
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='bottom', fontsize=8, color='black', xytext=(0, 5), textcoords='offset points')
    plt.tight_layout()
    plt.savefig(f'/main/DL/draw/outcome_categories_{dataset_name}.png', bbox_inches='tight')
    plt.close()

def load_dataSet(path):
    df_0 = pd.read_csv(path, header=0)
    return df_0

def save_stats_to_txt(means, stds, feature_columns, means_path="./mean_std/means.txt", stds_path="./mean_std/stds.txt"):
    with open(means_path, 'w', encoding='utf-8') as f:
        for col, mean in zip(feature_columns, means):
            f.write(f"{col}: {mean}\n")

    with open(stds_path, 'w', encoding='utf-8') as f:
        for col, std in zip(feature_columns, stds):
            f.write(f"{col}: {std}\n")

    print(f"均值已保存至: {means_path}")
    print(f"标准差已保存至: {stds_path}")

def preprocess_data(train_df):
    train_df = train_df.copy()

    label_encoder = LabelEncoder()
    train_df[' Label'] = label_encoder.fit_transform(train_df[' Label'])
    class_names = label_encoder.classes_
    
    with open("./mean_std/class_names.txt", 'w', encoding='utf-8') as f:
        for name in class_names:
            f.write(f"{name}\n")

    X_train_df = train_df.drop(columns=[' Label'])
    y_train = train_df[' Label'].values

    if X_train_df.isna().any().any() or np.isinf(X_train_df.values).any():
        print("警告：数据中存在 NaN 或 inf，正在处理...")
        X_train_df = X_train_df.replace([np.inf, -np.inf], np.nan).fillna(0)

    means = X_train_df.mean()
    stds = X_train_df.std()
    stds = stds.replace(0, 1).fillna(1)

    X_train = (X_train_df - means) / stds
    X_train = X_train.fillna(0)

    if np.isinf(X_train.values).any():
        print("警告：标准化后仍存在 inf 值，请检查数据范围或分布！")

    train_feature_columns = X_train_df.columns.tolist()
    save_stats_to_txt(means, stds, train_feature_columns)

    return X_train, y_train, train_df, class_names

def load_array(data_arrays, batch_size, is_Train=True):
    dataset = TensorDataset(*data_arrays)
    return DataLoader(dataset, batch_size, shuffle=is_Train)

class Attention(nn.Module):
    def __init__(self, hidden_size):
        super(Attention, self).__init__()
        self.hidden_size = hidden_size
        self.attention = nn.Linear(hidden_size, 1)
        
    def forward(self, lstm_output):
        # lstm_output shape: (batch_size, seq_len, hidden_size)
        attention_weights = F.softmax(self.attention(lstm_output), dim=1)
        # attention_weights shape: (batch_size, seq_len, 1)
        context = torch.sum(attention_weights * lstm_output, dim=1)
        # context shape: (batch_size, hidden_size)
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
        # 输入形状: (batch_size, input_size)
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

def train_model(net, train_iter, valid_iter, num_epochs, lr, wd, n_valid_size):
    trainer = torch.optim.Adam(net.parameters(), lr=lr, weight_decay=wd)
    numbers_batch = len(train_iter)
    net = net.to(device)
    best_accuracy = 0.0
    
    for epoch in range(num_epochs):
        print("-------第 {} 轮训练开始-------".format(epoch + 1))
        net.train()
        total_train_loss = 0
        total_train_correct = 0
        total_train_samples = 0
        num_batches = 0

        for i, (features, labels) in enumerate(train_iter):
            features = features.to(device)
            labels = labels.to(device)
            trainer.zero_grad()
            pred = net(features)
            l = loss_fn(pred, labels)
            l.backward()
            trainer.step()

            total_train_loss += l.item()
            _, predicted = torch.max(pred, 1)
            total_train_correct += (predicted == labels).sum().item()
            total_train_samples += labels.size(0)
            num_batches += 1

            if (i + 1) % (numbers_batch // 5) == 0 or i == numbers_batch - 1:
                print(f'epoch {epoch + 1}, iter {i + 1}: train loss {l.item():.3f}')

        avg_train_loss = total_train_loss / num_batches
        train_accuracy = total_train_correct / total_train_samples * 100

        total_valid_loss = 0
        total_valid_correct = 0
        total_valid_samples = 0
        num_valid_batches = 0

        if valid_iter is not None:
            net.eval()
            with torch.no_grad():
                for X, y in valid_iter:
                    X = X.to(device)
                    targets = y.to(device)
                    output = net(X)
                    loss = loss_fn(output, targets)
                    total_valid_loss += loss.item()
                    _, predicted = torch.max(output, 1)
                    total_valid_correct += (predicted == targets).sum().item()
                    total_valid_samples += targets.size(0)
                    num_valid_batches += 1

            avg_valid_loss = total_valid_loss / num_valid_batches
            valid_accuracy = total_valid_correct / total_valid_samples * 100

            print(f"Epoch {epoch + 1}, Train Loss: {avg_train_loss:.3f}, Train Accuracy: {train_accuracy:.2f}%, "
                  f"Valid Loss: {avg_valid_loss:.3f}, Valid Accuracy: {valid_accuracy:.2f}%")

            writer_train.add_scalar('Loss', avg_train_loss, epoch)
            writer_train.add_scalar('Accuracy', train_accuracy, epoch)
            writer_valid.add_scalar('Loss', avg_valid_loss, epoch)
            writer_valid.add_scalar('Accuracy', valid_accuracy, epoch)

            if valid_accuracy > best_accuracy:
                best_accuracy = valid_accuracy
                best_epoch = epoch
                torch.save(net.state_dict(), r"model/best_model_cnn_lstm_attention.pth")
                print(f"新最佳模型已保存，准确率: {best_accuracy:.3f}, epoch: {best_epoch + 1}")

    writer_train.close()
    writer_valid.close()
    return train_accuracy, avg_valid_loss

def test_model(test_iter, model):
    model.eval()
    all_preds = []
    all_labels = []
    with torch.no_grad():
        for inputs, labels in test_iter:
            inputs = inputs.to(device)
            labels = labels.to(device)
            outputs = model(inputs)
            predicted = outputs.argmax(dim=1)
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    accuracy = accuracy_score(all_labels, all_preds)
    precision = precision_score(all_labels, all_preds, average='weighted', zero_division=0)
    recall = recall_score(all_labels, all_preds, average='weighted', zero_division=0)
    f1 = f1_score(all_labels, all_preds, average='weighted', zero_division=0)

    print(f'Accuracy: {accuracy:.3f}')
    print(f'Precision (weighted): {precision:.3f}')
    print(f'Recall (weighted): {recall:.3f}')
    print(f'F1-Score (weighted): {f1:.3f}')

    return accuracy, precision, recall, f1, all_preds, all_labels

def plot_confusion_matrix(y_true, y_pred, class_names):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(r'main/DL/draw/confusion_matrix_cnn_lstm_att.png', dpi=300, bbox_inches='tight')
    plt.close()

def main_attention(num_epochs=1, lr=5e-4, wd=1e-5, batch_size=256):
    data_df = load_dataSet(r"main/DL/data/cic2017_train.csv")
    train_features, train_labels, original_df, class_names = preprocess_data(data_df)

    feature_type_count = train_features.shape[1]

    train_features, train_labels = shuffle(train_features, train_labels, random_state=42)
    train_ratio, valid_ratio, test_ratio = 0.7, 0.15, 0.15
    n_samples = train_features.shape[0]
    n_train = int(n_samples * train_ratio)
    n_valid = int(n_samples * valid_ratio)
    n_test = n_samples - n_train - n_valid
    valid_features, valid_labels = train_features[:n_valid], train_labels[:n_valid]
    test_features, test_labels = train_features[n_valid:n_valid + n_test], train_labels[n_valid:n_valid + n_test]

    train_features_tensor = torch.tensor(train_features.values, dtype=torch.float32)
    train_labels_tensor = torch.tensor(train_labels, dtype=torch.long)
    valid_features_tensor = torch.tensor(valid_features.values, dtype=torch.float32)
    valid_labels_tensor = torch.tensor(valid_labels, dtype=torch.long)
    test_features_tensor = torch.tensor(test_features.values, dtype=torch.float32)
    test_labels_tensor = torch.tensor(test_labels, dtype=torch.long)

    train_iter = load_array((train_features_tensor, train_labels_tensor), batch_size)
    valid_iter = load_array((valid_features_tensor, valid_labels_tensor), batch_size)
    test_iter = load_array((test_features_tensor, test_labels_tensor), batch_size, False)

    net = CNN_LSTM_Attention_Model(
        input_size=feature_type_count,
        num_classes=len(class_names)
    )
    train_accuracy, valid_loss = train_model(net, train_iter, valid_iter, num_epochs, lr, wd, n_valid)
    test_accuracy, test_precision, test_recall, test_f1, test_preds, test_labels = test_model(test_iter, net)

    plot_confusion_matrix(test_labels, test_preds, class_names)

    from sklearn.metrics import classification_report
    from tabulate import tabulate

    print("\n详细分类报告：")
    report = classification_report(
        test_labels,
        test_preds,
        target_names=class_names,
        output_dict=True
    )

    report_df = pd.DataFrame(report).transpose()
    print(tabulate(
        report_df,
        headers="keys",
        tablefmt="psql",
        floatfmt=".3f",
        numalign="center",
        stralign="center"
    ))

    return test_accuracy, test_precision, test_recall, test_f1 