@echo off
chcp 65001 >nul
echo ================================================================
echo 深度学习网络流量异常检测系统 - 快速测试
echo ================================================================
echo.

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python
    pause
    exit /b 1
)

echo 检查Django服务器连接...
python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000', timeout=3)" >nul 2>&1
if errorlevel 1 (
    echo 错误: Django服务器未运行，请先启动服务器
    echo 启动命令: python manage.py runserver 127.0.0.1:8000
    pause
    exit /b 1
)

echo ✓ Django服务器运行正常
echo.

echo 开始攻击测试...
python basic_test.py

echo.
echo 测试完成！
echo.
echo 查看检测结果:
echo 1. 打开浏览器访问: http://127.0.0.1:8000/admin/main/trafficlog/
echo 2. 用户名: admin
echo 3. 密码: admin
echo.
echo 按任意键打开管理后台...
pause >nul

start http://127.0.0.1:8000/admin/main/trafficlog/
