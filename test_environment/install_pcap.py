#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装和配置网络包捕获库
"""

import os
import sys
import subprocess
import platform
import urllib.request
import tempfile

def check_admin_rights():
    """检查是否有管理员权限"""
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except:
        return False

def install_npcap_windows():
    """在Windows上安装Npcap"""
    print("检测到Windows系统，准备安装Npcap...")
    
    if not check_admin_rights():
        print("错误: 需要管理员权限来安装Npcap")
        print("请以管理员身份运行此脚本")
        return False
    
    # Npcap下载URL
    npcap_url = "https://nmap.org/npcap/dist/npcap-1.75.exe"
    
    try:
        print("正在下载Npcap安装程序...")
        with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp_file:
            urllib.request.urlretrieve(npcap_url, tmp_file.name)
            installer_path = tmp_file.name
        
        print("正在安装Npcap...")
        # 静默安装Npcap
        result = subprocess.run([installer_path, '/S'], capture_output=True, text=True)
        
        # 清理临时文件
        os.unlink(installer_path)
        
        if result.returncode == 0:
            print("✓ Npcap安装成功")
            return True
        else:
            print(f"✗ Npcap安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ 下载或安装Npcap时出错: {e}")
        return False

def install_libpcap_linux():
    """在Linux上安装libpcap"""
    print("检测到Linux系统，准备安装libpcap...")
    
    try:
        # 尝试使用apt-get (Ubuntu/Debian)
        result = subprocess.run(['sudo', 'apt-get', 'update'], capture_output=True)
        if result.returncode == 0:
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'libpcap-dev'])
            print("✓ libpcap安装成功 (apt-get)")
            return True
    except:
        pass
    
    try:
        # 尝试使用yum (CentOS/RHEL)
        subprocess.run(['sudo', 'yum', 'install', '-y', 'libpcap-devel'])
        print("✓ libpcap安装成功 (yum)")
        return True
    except:
        pass
    
    try:
        # 尝试使用dnf (Fedora)
        subprocess.run(['sudo', 'dnf', 'install', '-y', 'libpcap-devel'])
        print("✓ libpcap安装成功 (dnf)")
        return True
    except:
        pass
    
    print("✗ 无法自动安装libpcap，请手动安装")
    return False

def test_scapy_pcap():
    """测试Scapy是否可以使用pcap"""
    try:
        from scapy.all import get_if_list
        interfaces = get_if_list()
        
        if interfaces:
            print(f"✓ Scapy可以正常工作，发现 {len(interfaces)} 个网络接口")
            print("可用接口:")
            for i, iface in enumerate(interfaces[:5]):  # 只显示前5个
                print(f"  {i+1}. {iface}")
            if len(interfaces) > 5:
                print(f"  ... 还有 {len(interfaces) - 5} 个接口")
            return True
        else:
            print("✗ Scapy无法发现网络接口")
            return False
            
    except ImportError:
        print("✗ Scapy未安装")
        return False
    except Exception as e:
        print(f"✗ Scapy测试失败: {e}")
        return False

def install_python_packages():
    """安装必要的Python包"""
    packages = ['scapy', 'psutil']
    
    for package in packages:
        try:
            print(f"安装 {package}...")
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ {package} 安装成功")
            else:
                print(f"✗ {package} 安装失败: {result.stderr}")
        except Exception as e:
            print(f"✗ 安装 {package} 时出错: {e}")

def main():
    print("=" * 60)
    print("网络包捕获库安装工具")
    print("=" * 60)
    
    system = platform.system()
    print(f"检测到操作系统: {system}")
    
    # 1. 安装Python包
    print("\n步骤1: 安装Python包")
    install_python_packages()
    
    # 2. 安装系统级别的pcap库
    print("\n步骤2: 安装系统级pcap库")
    if system == "Windows":
        success = install_npcap_windows()
    elif system == "Linux":
        success = install_libpcap_linux()
    elif system == "Darwin":  # macOS
        print("macOS通常已经包含libpcap，无需额外安装")
        success = True
    else:
        print(f"不支持的操作系统: {system}")
        success = False
    
    # 3. 测试安装结果
    print("\n步骤3: 测试安装结果")
    if test_scapy_pcap():
        print("\n✓ 所有组件安装成功！")
        print("现在可以运行网络流量检测系统了")
    else:
        print("\n✗ 安装可能存在问题")
        print("建议:")
        if system == "Windows":
            print("1. 手动下载并安装Npcap: https://nmap.org/npcap/")
            print("2. 重启计算机")
            print("3. 以管理员身份运行Python脚本")
        else:
            print("1. 手动安装libpcap开发包")
            print("2. 确保有足够的权限访问网络接口")

if __name__ == "__main__":
    main()
