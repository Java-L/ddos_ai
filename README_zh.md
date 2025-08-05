# 深度学习网络流量异常检测系统

基于Django的深度学习系统，使用CNN、LSTM和注意力机制检测网络流量异常和DDoS攻击。

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Windows/Linux/macOS
- 管理员权限（用于网络数据包捕获）

### 1. 安装依赖
```bash
# 从依赖文件安装
pip install -r requirements.txt

# 或手动安装
pip install django==5.1.4 torch torchvision numpy pandas matplotlib seaborn scikit-learn scapy requests django-simple-captcha
```

### 2. 设置数据库
```bash
cd df_defence
python manage.py migrate
python manage.py collectstatic --noinput
```

### 3. 创建超级用户
```bash
python manage.py createsuperuser
# 按提示创建管理员账户
```

### 4. 启动应用
```bash
python manage.py runserver 127.0.0.1:8000
```

### 5. 访问系统
- **主应用**: http://127.0.0.1:8000/
- **管理面板**: http://127.0.0.1:8000/admin/
- **流量日志**: http://127.0.0.1:8000/traffic-log/

## 🏗️ 系统架构

### 核心组件
- **DDoS检测中间件**: 实时流量分析和攻击检测
- **深度学习模型**: CNN、LSTM和CNN-LSTM-Attention分类模型
- **流量监控器**: 网络数据包捕获和特征提取
- **Web界面**: 基于Django的管理和可视化

### 支持的攻击类型
- **DoS/DDoS**: 拒绝服务攻击
- **端口扫描**: 网络侦察
- **Web攻击**: SQL注入、XSS、路径遍历
- **僵尸网络**: C&C通信模式
- **渗透攻击**: 暴力破解和渗透尝试
- **心脏滴血**: SSL/TLS漏洞利用

## 🧪 测试环境

### 自动化测试
```bash
# 运行完整攻防测试
cd test_environment
python run_test.py
```

### 手动攻击模拟
```bash
# 模拟所有攻击类型
python attack_simulator.py --attack all --normal

# 特定攻击类型
python attack_simulator.py --attack dos
python attack_simulator.py --attack scan
python attack_simulator.py --attack web

# 自定义目标
python attack_simulator.py --target 192.168.1.100 --port 8080
```

### 流量生成
```bash
# 生成混合流量
python traffic_generator.py --type all --duration 120

# 仅正常流量
python traffic_generator.py --type benign --duration 60
```

### Windows快速启动
```batch
# 双击运行或在命令提示符中执行
test_environment\start_test.bat
```

## 📊 模型管理

### 可用模型
- **CNN模型**: 卷积神经网络用于空间特征提取
- **LSTM模型**: 长短期记忆网络用于时序模式识别
- **CNN-LSTM-Attention**: 带注意力机制的混合模型

### 模型训练和调优
```bash
# 访问模型调优界面
http://127.0.0.1:8000/model-tuning/

# 使用自定义数据集训练新模型
# 通过Web界面调整超参数
# 监控训练进度和指标
```

## 🔍 监控与分析

### 实时检测
- 通过DDoS中间件进行实时流量监控
- 自动威胁分类和评分
- 高风险活动实时警报

### 结果分析
```bash
# 分析检测结果
cd test_environment
python analyze_results.py --hours 24 --show

# 生成详细报告
python analyze_results.py --db ../db.sqlite3
```

### Web仪表板
- **流量日志**: http://127.0.0.1:8000/admin/main/trafficlog/
- **IP规则**: http://127.0.0.1:8000/admin/main/ipaddressrule/
- **模型状态**: http://127.0.0.1:8000/admin/main/tuningmodels/

## 🛠️ 配置

### Django设置
关键配置文件：
- `df_defence/dl_ids/settings.py` - Django主设置
- `df_defence/main/config.py` - 应用特定配置
- `df_defence/main/ddos_middleware.py` - 检测参数

### 检测阈值
```python
# 在ddos_middleware.py中修改
RATE_LIMIT_THRESHOLD = 100  # 每分钟请求数
BURST_THRESHOLD = 20        # 10秒内突发请求数
CONNECTION_LIMIT = 50       # 最大并发连接数
```

### 模型路径
```python
# 模型文件位置
df_defence/model/
├── best_model_cnn.pth
├── best_model_lstm.pth
└── best_model_cnn_lstm_attention.pth
```

## 🚨 安全注意事项

### 测试环境
- **使用隔离网络**进行攻击模拟
- **不要在生产系统上测试**
- **确保有适当授权**再进行测试

### 法律合规
- 仅在拥有或有明确许可的系统上测试
- 遵守当地网络安全法律法规
- 记录所有测试活动

### 网络影响
- 攻击模拟会产生大量流量
- 可能触发监控系统的安全警报
- 确保系统资源充足

## 🔧 故障排除

### 常见问题

#### Django服务器无法启动
```bash
# 检查端口可用性
netstat -an | findstr 8000

# 验证数据库设置
python manage.py migrate
python manage.py check

# 测试Django基本安装
python -c "import django; print(django.get_version())"
```

#### 权限错误（Scapy）
```bash
# Windows: 以管理员身份运行
# Linux/macOS: 使用sudo
sudo python manage.py runserver 127.0.0.1:8000

# 或在Windows上安装WinPcap/Npcap
# 在Linux上安装libpcap-dev
```

#### 缺少依赖
```bash
# 重新安装依赖
pip install -r requirements.txt

# 检查特定包
python -c "import torch; print('PyTorch OK')"
python -c "from scapy.all import *; print('Scapy OK')"
```

#### 无检测结果
1. 检查中间件是否在`settings.py`中加载
2. 验证模型文件是否存在于`model/`目录
3. 确保流量到达Django服务器
4. 检查Django日志错误

### 性能问题
- **CPU使用率高**: 降低检测频率或模型复杂度
- **内存泄漏**: 在重度测试期间定期重启服务器
- **响应慢**: 检查数据库性能和索引

## 📁 项目结构

```
df_defence/
├── manage.py                 # Django管理脚本
├── db.sqlite3               # SQLite数据库
├── requirements.txt         # Python依赖
├── dl_ids/                  # Django项目设置
│   ├── settings.py         # 主配置
│   ├── urls.py             # URL路由
│   └── wsgi.py             # WSGI配置
├── main/                    # 主应用
│   ├── models.py           # 数据库模型
│   ├── views.py            # Web视图
│   ├── ddos_middleware.py  # DDoS检测中间件
│   ├── DL/                 # 深度学习模块
│   └── monitorTraffic/     # 流量监控
├── model/                   # 预训练模型
│   ├── best_model_cnn.pth
│   ├── best_model_lstm.pth
│   └── best_model_cnn_lstm_attention.pth
├── templates/               # HTML模板
├── static/                  # 静态文件（CSS、JS）
└── test_environment/        # 测试工具
    ├── run_test.py         # 主测试运行器
    ├── attack_simulator.py # 攻击模拟
    ├── traffic_generator.py # 流量生成
    └── analyze_results.py  # 结果分析
```

## 🤝 贡献

### 开发设置
1. Fork仓库
2. 创建虚拟环境
3. 安装开发依赖
4. 提交更改前运行测试

### 添加新攻击类型
1. 扩展`attack_simulator.py`
2. 更新`ddos_middleware.py`中的检测逻辑
3. 添加相应的模型训练数据
4. 更新文档

## 📄 许可证

本项目用于教育和研究目的。使用攻击模拟功能时请确保遵守当地法律法规。

## 📞 支持

技术支持或问题咨询：
- 查看上述故障排除部分
- 检查Django日志获取错误详情
- 确保所有依赖正确安装
- 验证网络连接和权限
