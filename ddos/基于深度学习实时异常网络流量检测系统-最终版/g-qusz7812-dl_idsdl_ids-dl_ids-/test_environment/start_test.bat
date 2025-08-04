@echo off
chcp 65001 >nul
echo ================================================================
echo 深度学习网络流量异常检测系统 - 攻防环境测试
echo ================================================================
echo.

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

echo 检查当前目录...
if not exist "run_test.py" (
    echo 错误: 请在test_environment目录下运行此脚本
    pause
    exit /b 1
)

echo.
echo 选择测试模式:
echo 1. 完整自动化测试 (推荐)
echo 2. 仅启动攻击模拟器
echo 3. 仅生成流量
echo 4. 查看帮助
echo.
set /p choice="请输入选择 (1-4): "

if "%choice%"=="1" goto full_test
if "%choice%"=="2" goto attack_only
if "%choice%"=="3" goto traffic_only
if "%choice%"=="4" goto show_help
goto invalid_choice

:full_test
echo.
echo 启动完整自动化测试...
echo 注意: 请确保以管理员权限运行此脚本
echo.
python run_test.py
goto end

:attack_only
echo.
echo 启动攻击模拟器...
echo 请确保Django服务器已在 127.0.0.1:8000 运行
echo.
set /p confirm="确认继续? (y/n): "
if /i "%confirm%"=="y" (
    python attack_simulator.py --attack all --normal
) else (
    echo 已取消
)
goto end

:traffic_only
echo.
echo 启动流量生成器...
echo 请确保Django服务器已在 127.0.0.1:8000 运行
echo.
set /p duration="请输入生成时长(秒，默认60): "
if "%duration%"=="" set duration=60
python traffic_generator.py --type all --duration %duration%
goto end

:show_help
echo.
echo ================================================================
echo 使用说明:
echo ================================================================
echo.
echo 1. 完整自动化测试:
echo    - 自动启动Django服务器
echo    - 等待用户确认准备就绪
echo    - 启动攻击模拟和流量生成
echo    - 监控系统状态
echo    - 显示测试结果
echo.
echo 2. 仅启动攻击模拟器:
echo    - 需要手动启动Django服务器
echo    - 执行各种网络攻击模拟
echo    - 同时生成正常流量
echo.
echo 3. 仅生成流量:
echo    - 需要手动启动Django服务器
echo    - 生成各种类型的网络流量
echo    - 可指定生成时长
echo.
echo 4. 手动启动Django服务器:
echo    cd ..
echo    python manage.py runserver 127.0.0.1:8000
echo.
echo 5. 查看检测结果:
echo    http://127.0.0.1:8000/admin/
echo    用户名: admin
echo    密码: admin
echo.
echo ================================================================
pause
goto end

:invalid_choice
echo 无效选择，请重新运行脚本
pause
goto end

:end
echo.
echo 测试完成，按任意键退出...
pause >nul
