# Npcap安装指南

## 什么是Npcap？
Npcap是WinPcap的现代替代品，为Windows提供网络包捕获功能。

## 安装步骤

### 1. 下载Npcap
- 访问官网: https://npcap.com/#download
- 下载最新版本的Npcap安装程序

### 2. 安装配置
运行安装程序时，确保勾选以下选项：
- ✅ "Install Npcap in WinPcap API-compatible Mode"
- ✅ "Support raw 802.11 traffic"

### 3. 重启系统
安装完成后重启计算机以确保驱动正确加载。

### 4. 验证安装
```bash
# 在Python中测试
python -c "from scapy.all import *; print('Npcap安装成功!')"
```

## 注意事项
- 需要管理员权限安装
- 可能需要关闭防病毒软件
- 安装后需要重启系统
