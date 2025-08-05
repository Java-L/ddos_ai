@echo off
chcp 65001 >nul
echo ================================================================
echo Deep Learning Network Traffic Anomaly Detection System
echo Dependency Installation Script for Windows
echo 深度学习网络流量异常检测系统 Windows依赖安装脚本
echo ================================================================
echo.

echo Checking Python installation... / 检查Python安装...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python not found. Please install Python 3.8+ first.
    echo ❌ 错误：未找到Python。请先安装Python 3.8+。
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found / Python已找到
python --version

echo.
echo Checking pip installation... / 检查pip安装...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: pip not found. Please install pip first.
    echo ❌ 错误：未找到pip。请先安装pip。
    pause
    exit /b 1
)

echo ✅ pip found / pip已找到

echo.
echo ⚠️  IMPORTANT NOTICE / 重要提示:
echo For network packet capture functionality, you need to install Npcap:
echo 为了使用网络数据包捕获功能，您需要安装Npcap：
echo Download from: https://npcap.com/
echo.
set /p install_npcap="Have you installed Npcap? (y/n) / 您是否已安装Npcap？(y/n): "
if /i not "%install_npcap%"=="y" (
    echo.
    echo Please install Npcap first, then run this script again.
    echo 请先安装Npcap，然后重新运行此脚本。
    echo Opening Npcap download page... / 正在打开Npcap下载页面...
    start https://npcap.com/
    pause
    exit /b 1
)

echo.
echo Upgrading pip... / 升级pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ⚠️  Warning: Failed to upgrade pip / 警告：升级pip失败
)

echo.
echo Installing Python dependencies... / 安装Python依赖...
echo This may take several minutes... / 这可能需要几分钟...

if not exist "requirements.txt" (
    echo ❌ Error: requirements.txt not found
    echo ❌ 错误：未找到requirements.txt文件
    pause
    exit /b 1
)

python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error: Failed to install dependencies
    echo ❌ 错误：安装依赖失败
    echo.
    echo Common solutions / 常见解决方案:
    echo 1. Run as Administrator / 以管理员身份运行
    echo 2. Check internet connection / 检查网络连接
    echo 3. Try: pip install --user -r requirements.txt
    pause
    exit /b 1
)

echo.
echo ✅ Dependencies installed successfully / 依赖安装成功

echo.
echo Verifying installation... / 验证安装...

echo Testing Django...
python -c "import django; print('✅ Django:', django.get_version())" 2>nul
if errorlevel 1 echo ❌ Django installation failed

echo Testing PyTorch...
python -c "import torch; print('✅ PyTorch:', torch.__version__)" 2>nul
if errorlevel 1 echo ❌ PyTorch installation failed

echo Testing Scapy...
python -c "from scapy.all import *; print('✅ Scapy: OK')" 2>nul
if errorlevel 1 echo ❌ Scapy installation failed - Check Npcap installation

echo Testing NumPy...
python -c "import numpy; print('✅ NumPy:', numpy.__version__)" 2>nul
if errorlevel 1 echo ❌ NumPy installation failed

echo Testing Pandas...
python -c "import pandas; print('✅ Pandas:', pandas.__version__)" 2>nul
if errorlevel 1 echo ❌ Pandas installation failed

echo.
echo Setting up Django application... / 设置Django应用...

if not exist "df_defence" (
    echo ❌ Error: df_defence directory not found
    echo ❌ 错误：未找到df_defence目录
    pause
    exit /b 1
)

cd df_defence

echo Running database migrations... / 运行数据库迁移...
python manage.py migrate
if errorlevel 1 (
    echo ⚠️  Warning: Database migration failed / 警告：数据库迁移失败
)

echo Collecting static files... / 收集静态文件...
python manage.py collectstatic --noinput
if errorlevel 1 (
    echo ⚠️  Warning: Static files collection failed / 警告：静态文件收集失败
)

cd ..

echo.
echo ================================================================
echo 🎉 Installation completed successfully! / 安装成功完成！
echo ================================================================
echo.
echo Next steps / 下一步:
echo 1. Create superuser / 创建超级用户:
echo    cd df_defence
echo    python manage.py createsuperuser
echo.
echo 2. Start the application / 启动应用:
echo    python manage.py runserver 127.0.0.1:8000
echo.
echo 3. Access the system / 访问系统:
echo    Main App / 主应用: http://127.0.0.1:8000/
echo    Admin Panel / 管理面板: http://127.0.0.1:8000/admin/
echo.
echo 4. Run tests / 运行测试:
echo    cd test_environment
echo    python run_test.py
echo.
echo ================================================================

pause
