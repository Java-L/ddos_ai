#!/bin/bash

# Deep Learning Network Traffic Anomaly Detection System
# Dependency Installation Script for Linux/macOS
# 深度学习网络流量异常检测系统 Linux/macOS依赖安装脚本

set -e  # Exit on any error

echo "================================================================"
echo "Deep Learning Network Traffic Anomaly Detection System"
echo "Dependency Installation Script for Linux/macOS"
echo "深度学习网络流量异常检测系统 Linux/macOS依赖安装脚本"
echo "================================================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_warning "This script should not be run as root for security reasons"
   print_warning "出于安全考虑，此脚本不应以root身份运行"
   echo "Please run as a regular user with sudo privileges"
   echo "请以具有sudo权限的普通用户身份运行"
   exit 1
fi

# Check Python version
echo "Checking Python installation... / 检查Python安装..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    PYTHON_CMD="python3"
    print_success "Python3 found: $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    PYTHON_CMD="python"
    print_success "Python found: $PYTHON_VERSION"
else
    print_error "Python not found. Please install Python 3.8+ first."
    print_error "未找到Python。请先安装Python 3.8+。"
    exit 1
fi

# Check Python version is 3.8+
if ! $PYTHON_CMD -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)' 2>/dev/null; then
    print_error "Python 3.8 or higher is required. Current version: $PYTHON_VERSION"
    print_error "需要Python 3.8或更高版本。当前版本：$PYTHON_VERSION"
    exit 1
fi

# Check pip
echo
echo "Checking pip installation... / 检查pip安装..."
if $PYTHON_CMD -m pip --version &> /dev/null; then
    print_success "pip found"
else
    print_error "pip not found. Please install pip first."
    print_error "未找到pip。请先安装pip。"
    exit 1
fi

# Detect OS and install system dependencies
echo
echo "Installing system dependencies... / 安装系统依赖..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    print_success "Detected Linux system"
    
    # Check if apt is available (Debian/Ubuntu)
    if command -v apt-get &> /dev/null; then
        echo "Installing libpcap-dev and python3-dev..."
        sudo apt-get update
        sudo apt-get install -y libpcap-dev python3-dev python3-pip
        print_success "Linux system dependencies installed"
    
    # Check if yum is available (RHEL/CentOS)
    elif command -v yum &> /dev/null; then
        echo "Installing libpcap-devel and python3-devel..."
        sudo yum install -y libpcap-devel python3-devel python3-pip
        print_success "Linux system dependencies installed"
    
    # Check if dnf is available (Fedora)
    elif command -v dnf &> /dev/null; then
        echo "Installing libpcap-devel and python3-devel..."
        sudo dnf install -y libpcap-devel python3-devel python3-pip
        print_success "Linux system dependencies installed"
    
    else
        print_warning "Unknown Linux distribution. Please install libpcap development packages manually."
        print_warning "未知的Linux发行版。请手动安装libpcap开发包。"
    fi

elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    print_success "Detected macOS system"
    
    # Check if Homebrew is installed
    if command -v brew &> /dev/null; then
        echo "Installing libpcap via Homebrew..."
        brew install libpcap
        print_success "macOS system dependencies installed"
    else
        print_warning "Homebrew not found. Please install Homebrew first:"
        print_warning "未找到Homebrew。请先安装Homebrew："
        echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        echo "Then run: brew install libpcap"
    fi

else
    print_warning "Unknown operating system: $OSTYPE"
    print_warning "未知操作系统：$OSTYPE"
fi

# Upgrade pip
echo
echo "Upgrading pip... / 升级pip..."
$PYTHON_CMD -m pip install --upgrade pip --user

# Install Python dependencies
echo
echo "Installing Python dependencies... / 安装Python依赖..."
echo "This may take several minutes... / 这可能需要几分钟..."

if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found"
    print_error "未找到requirements.txt文件"
    exit 1
fi

$PYTHON_CMD -m pip install -r requirements.txt --user

print_success "Dependencies installed successfully"

# Verify installation
echo
echo "Verifying installation... / 验证安装..."

verify_package() {
    local package=$1
    local display_name=$2
    
    if $PYTHON_CMD -c "import $package" 2>/dev/null; then
        print_success "$display_name: OK"
        return 0
    else
        print_error "$display_name: Failed"
        return 1
    fi
}

FAILED=0

verify_package "django" "Django" || FAILED=1
verify_package "torch" "PyTorch" || FAILED=1
verify_package "numpy" "NumPy" || FAILED=1
verify_package "pandas" "Pandas" || FAILED=1
verify_package "requests" "Requests" || FAILED=1
verify_package "matplotlib" "Matplotlib" || FAILED=1
verify_package "sklearn" "Scikit-learn" || FAILED=1

# Special check for Scapy (may require root privileges)
echo "Testing Scapy..."
if $PYTHON_CMD -c "from scapy.all import *" 2>/dev/null; then
    print_success "Scapy: OK"
else
    print_warning "Scapy: May require root privileges for packet capture"
    print_warning "Scapy：数据包捕获可能需要root权限"
fi

if [ $FAILED -eq 1 ]; then
    print_error "Some packages failed to install. Please check the errors above."
    print_error "某些包安装失败。请检查上面的错误信息。"
    exit 1
fi

# Setup Django
echo
echo "Setting up Django application... / 设置Django应用..."

if [ ! -d "df_defence" ]; then
    print_error "df_defence directory not found"
    print_error "未找到df_defence目录"
    exit 1
fi

cd df_defence

echo "Running database migrations... / 运行数据库迁移..."
$PYTHON_CMD manage.py migrate

echo "Collecting static files... / 收集静态文件..."
$PYTHON_CMD manage.py collectstatic --noinput

cd ..

print_success "Django setup completed"

echo
echo "================================================================"
echo "🎉 Installation completed successfully! / 安装成功完成！"
echo "================================================================"
echo
echo "Next steps / 下一步:"
echo "1. Create superuser / 创建超级用户:"
echo "   cd df_defence"
echo "   $PYTHON_CMD manage.py createsuperuser"
echo
echo "2. Start the application / 启动应用:"
echo "   $PYTHON_CMD manage.py runserver 127.0.0.1:8000"
echo
echo "3. Access the system / 访问系统:"
echo "   Main App / 主应用: http://127.0.0.1:8000/"
echo "   Admin Panel / 管理面板: http://127.0.0.1:8000/admin/"
echo
echo "4. Run tests / 运行测试:"
echo "   cd test_environment"
echo "   $PYTHON_CMD run_test.py"
echo
echo "Note: For packet capture, you may need to run with sudo:"
echo "注意：对于数据包捕获，您可能需要使用sudo运行："
echo "   sudo $PYTHON_CMD manage.py runserver 127.0.0.1:8000"
echo
echo "================================================================"
