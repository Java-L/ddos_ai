#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dependency Installation Script for Deep Learning Network Traffic Anomaly Detection System
深度学习网络流量异常检测系统依赖安装脚本
"""

import os
import sys
import subprocess
import platform
import importlib.util

def check_python_version():
    """Check Python version / 检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print("❌ 错误：需要Python 3.8或更高版本")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python version check passed: {sys.version}")
    return True

def check_pip():
    """Check if pip is available / 检查pip是否可用"""
    try:
        import pip
        print("✅ pip is available")
        return True
    except ImportError:
        print("❌ Error: pip is not installed")
        print("❌ 错误：pip未安装")
        return False

def install_system_dependencies():
    """Install system-level dependencies / 安装系统级依赖"""
    system = platform.system().lower()
    
    print(f"\n🔧 Installing system dependencies for {system}...")
    print(f"🔧 为{system}安装系统依赖...")
    
    if system == "linux":
        print("Installing libpcap-dev and python3-dev...")
        try:
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "libpcap-dev", "python3-dev"], check=True)
            print("✅ Linux system dependencies installed")
        except subprocess.CalledProcessError:
            print("⚠️  Warning: Could not install system dependencies automatically")
            print("⚠️  警告：无法自动安装系统依赖")
            print("Please run manually: sudo apt-get install libpcap-dev python3-dev")
    
    elif system == "darwin":  # macOS
        print("Installing libpcap via Homebrew...")
        try:
            subprocess.run(["brew", "install", "libpcap"], check=True)
            print("✅ macOS system dependencies installed")
        except subprocess.CalledProcessError:
            print("⚠️  Warning: Could not install libpcap via Homebrew")
            print("⚠️  警告：无法通过Homebrew安装libpcap")
            print("Please install Homebrew and run: brew install libpcap")
    
    elif system == "windows":
        print("⚠️  Windows users need to install WinPcap or Npcap manually")
        print("⚠️  Windows用户需要手动安装WinPcap或Npcap")
        print("Download from: https://npcap.com/")

def install_python_dependencies():
    """Install Python dependencies / 安装Python依赖"""
    print("\n📦 Installing Python dependencies...")
    print("📦 安装Python依赖...")
    
    requirements_file = "requirements.txt"
    
    if not os.path.exists(requirements_file):
        print(f"❌ Error: {requirements_file} not found")
        print(f"❌ 错误：未找到{requirements_file}")
        return False
    
    try:
        # Upgrade pip first
        print("Upgrading pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        print(f"Installing from {requirements_file}...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_file], check=True)
        
        print("✅ Python dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print(f"❌ 安装依赖时出错：{e}")
        return False

def verify_installation():
    """Verify that key packages are installed / 验证关键包是否已安装"""
    print("\n🔍 Verifying installation...")
    print("🔍 验证安装...")
    
    required_packages = [
        ("django", "Django"),
        ("torch", "PyTorch"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("scapy", "Scapy"),
        ("requests", "Requests"),
        ("matplotlib", "Matplotlib"),
        ("sklearn", "Scikit-learn")
    ]
    
    failed_packages = []
    
    for package_name, display_name in required_packages:
        try:
            spec = importlib.util.find_spec(package_name)
            if spec is not None:
                print(f"✅ {display_name} - OK")
            else:
                print(f"❌ {display_name} - Not found")
                failed_packages.append(display_name)
        except ImportError:
            print(f"❌ {display_name} - Import error")
            failed_packages.append(display_name)
    
    if failed_packages:
        print(f"\n❌ Failed packages: {', '.join(failed_packages)}")
        print(f"❌ 安装失败的包：{', '.join(failed_packages)}")
        return False
    else:
        print("\n✅ All required packages are installed successfully!")
        print("✅ 所有必需的包都已成功安装！")
        return True

def setup_django():
    """Setup Django database and static files / 设置Django数据库和静态文件"""
    print("\n🔧 Setting up Django...")
    print("🔧 设置Django...")
    
    django_dir = "df_defence"
    
    if not os.path.exists(django_dir):
        print(f"❌ Error: Django directory '{django_dir}' not found")
        print(f"❌ 错误：未找到Django目录'{django_dir}'")
        return False
    
    try:
        os.chdir(django_dir)
        
        # Run migrations
        print("Running database migrations...")
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        
        # Collect static files
        print("Collecting static files...")
        subprocess.run([sys.executable, "manage.py", "collectstatic", "--noinput"], check=True)
        
        print("✅ Django setup completed")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error setting up Django: {e}")
        print(f"❌ 设置Django时出错：{e}")
        return False
    finally:
        os.chdir("..")

def main():
    """Main installation process / 主安装过程"""
    print("=" * 70)
    print("Deep Learning Network Traffic Anomaly Detection System")
    print("Dependency Installation Script")
    print("深度学习网络流量异常检测系统依赖安装脚本")
    print("=" * 70)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check pip
    if not check_pip():
        sys.exit(1)
    
    # Install system dependencies
    install_system_dependencies()
    
    # Install Python dependencies
    if not install_python_dependencies():
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("\n⚠️  Some packages failed to install. Please check the errors above.")
        print("⚠️  某些包安装失败。请检查上面的错误信息。")
        sys.exit(1)
    
    # Setup Django
    if not setup_django():
        print("\n⚠️  Django setup failed. You may need to run setup manually.")
        print("⚠️  Django设置失败。您可能需要手动运行设置。")
    
    print("\n" + "=" * 70)
    print("🎉 Installation completed successfully!")
    print("🎉 安装成功完成！")
    print("\nNext steps / 下一步:")
    print("1. cd df_defence")
    print("2. python manage.py createsuperuser")
    print("3. python manage.py runserver 127.0.0.1:8000")
    print("=" * 70)

if __name__ == "__main__":
    main()
