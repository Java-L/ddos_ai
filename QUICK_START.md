# Quick Start Guide / 快速启动指南

## 🚀 One-Click Installation / 一键安装

### Windows Users / Windows用户
```batch
# Double-click or run in Command Prompt / 双击或在命令提示符中运行
install_dependencies.bat
```

### Linux/macOS Users / Linux/macOS用户
```bash
# Make executable and run / 设置可执行权限并运行
chmod +x install_dependencies.sh
./install_dependencies.sh
```

### Python Script (All Platforms) / Python脚本（所有平台）
```bash
python install_dependencies.py
```

## 📋 Manual Installation / 手动安装

### Step 1: Install Dependencies / 步骤1：安装依赖
```bash
pip install -r requirements.txt
```

### Step 2: Setup Database / 步骤2：设置数据库
```bash
cd df_defence
python manage.py migrate
python manage.py collectstatic --noinput
```

### Step 3: Create Admin User / 步骤3：创建管理员用户
```bash
python manage.py createsuperuser
```

### Step 4: Start Application / 步骤4：启动应用
```bash
python manage.py runserver 127.0.0.1:8000
```

## 🔗 Access URLs / 访问地址

- **Main Application / 主应用**: http://127.0.0.1:8000/
- **Admin Panel / 管理面板**: http://127.0.0.1:8000/admin/
- **Traffic Logs / 流量日志**: http://127.0.0.1:8000/traffic-log/

## 🧪 Run Tests / 运行测试

### Automated Testing / 自动化测试
```bash
cd test_environment
python run_test.py
```

### Windows Quick Test / Windows快速测试
```batch
cd test_environment
start_test.bat
```

## ⚠️ Common Issues / 常见问题

### Permission Errors / 权限错误
- **Windows**: Run as Administrator / 以管理员身份运行
- **Linux/macOS**: Use `sudo` for packet capture / 使用`sudo`进行数据包捕获

### Missing Scapy Dependencies / 缺少Scapy依赖
- **Windows**: Install Npcap from https://npcap.com/
- **Linux**: `sudo apt-get install libpcap-dev`
- **macOS**: `brew install libpcap`

### Port Already in Use / 端口已被占用
```bash
# Check what's using port 8000 / 检查端口8000的使用情况
netstat -an | grep 8000  # Linux/macOS
netstat -an | findstr 8000  # Windows

# Use different port / 使用不同端口
python manage.py runserver 127.0.0.1:8080
```

## 📞 Need Help? / 需要帮助？

1. Check the full README.md for detailed instructions
2. Review the troubleshooting section
3. Ensure all dependencies are installed correctly
4. Verify network connectivity and permissions

1. 查看完整的README.md获取详细说明
2. 查看故障排除部分
3. 确保所有依赖都正确安装
4. 验证网络连接和权限
