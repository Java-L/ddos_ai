@echo off
chcp 65001 >nul
echo ================================================================
echo Deep Learning Network Traffic Anomaly Detection System - Attack-Defense Environment Test
echo 深度学习网络流量异常检测系统 - 攻防环境测试
echo ================================================================
echo.

echo Checking Python environment... / 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found, please ensure Python is installed and added to PATH
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

echo Checking current directory... / 检查当前目录...
if not exist "run_test.py" (
    echo Error: Please run this script in the test_environment directory
    echo 错误: 请在test_environment目录下运行此脚本
    pause
    exit /b 1
)

echo.
echo Select test mode / 选择测试模式:
echo 1. Full automated test (Recommended) / 完整自动化测试 (推荐)
echo 2. Attack simulator only / 仅启动攻击模拟器
echo 3. Traffic generator only / 仅生成流量
echo 4. Show help / 查看帮助
echo.
set /p choice="Please enter your choice (1-4) / 请输入选择 (1-4): "

if "%choice%"=="1" goto full_test
if "%choice%"=="2" goto attack_only
if "%choice%"=="3" goto traffic_only
if "%choice%"=="4" goto show_help
goto invalid_choice

:full_test
echo.
echo Starting full automated test... / 启动完整自动化测试...
echo Note: Please ensure this script is run with administrator privileges
echo 注意: 请确保以管理员权限运行此脚本
echo.
python run_test.py
goto end

:attack_only
echo.
echo Starting attack simulator... / 启动攻击模拟器...
echo Please ensure Django server is running at 127.0.0.1:8000
echo 请确保Django服务器已在 127.0.0.1:8000 运行
echo.
set /p confirm="Confirm to continue? (y/n) / 确认继续? (y/n): "
if /i "%confirm%"=="y" (
    python attack_simulator.py --attack all --normal
) else (
    echo Cancelled / 已取消
)
goto end

:traffic_only
echo.
echo Starting traffic generator... / 启动流量生成器...
echo Please ensure Django server is running at 127.0.0.1:8000
echo 请确保Django服务器已在 127.0.0.1:8000 运行
echo.
set /p duration="Enter generation duration in seconds (default 60) / 请输入生成时长(秒，默认60): "
if "%duration%"=="" set duration=60
python traffic_generator.py --type all --duration %duration%
goto end

:show_help
echo.
echo ================================================================
echo Usage Instructions / 使用说明:
echo ================================================================
echo.
echo 1. Full automated test / 完整自动化测试:
echo    - Automatically start Django server / 自动启动Django服务器
echo    - Wait for user confirmation / 等待用户确认准备就绪
echo    - Start attack simulation and traffic generation / 启动攻击模拟和流量生成
echo    - Monitor system status / 监控系统状态
echo    - Display test results / 显示测试结果
echo.
echo 2. Attack simulator only / 仅启动攻击模拟器:
echo    - Manually start Django server / 需要手动启动Django服务器
echo    - Execute various network attack simulations / 执行各种网络攻击模拟
echo    - Generate normal traffic simultaneously / 同时生成正常流量
echo.
echo 3. Traffic generator only / 仅生成流量:
echo    - Manually start Django server / 需要手动启动Django服务器
echo    - Generate various types of network traffic / 生成各种类型的网络流量
echo    - Specify generation duration / 可指定生成时长
echo.
echo 4. Manually start Django server / 手动启动Django服务器:
echo    cd ..
echo    python manage.py runserver 127.0.0.1:8000
echo.
echo 5. View detection results / 查看检测结果:
echo    http://127.0.0.1:8000/admin/
echo    Username / 用户名: admin
echo    Password / 密码: admin
echo.
echo ================================================================
pause
goto end

:invalid_choice
echo Invalid choice, please rerun the script / 无效选择，请重新运行脚本
pause
goto end

:end
echo.
echo Test completed, press any key to exit... / 测试完成，按任意键退出...
pause >nul
