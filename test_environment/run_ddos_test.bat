@echo off
chcp 65001 >nul
echo ================================================================
echo DDoS攻击检测测试 - 深度学习网络流量异常检测系统
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

echo ================================================================
echo 开始DDoS攻击测试...
echo ================================================================
echo 测试将包括以下攻击类型:
echo 1. HTTP洪水攻击 (高频HTTP请求)
echo 2. SYN洪水攻击 (TCP连接洪水)
echo 3. Slowloris攻击 (慢速连接攻击)
echo 4. UDP洪水攻击 (UDP数据包洪水)
echo.
echo 测试期间请不要关闭此窗口...
echo.

python ddos_attack_test.py

echo.
echo ================================================================
echo DDoS攻击测试完成！
echo ================================================================
echo.
echo 查看检测结果:
echo 1. 打开浏览器访问: http://127.0.0.1:8000/admin/main/trafficlog/
echo 2. 用户名: admin
echo 3. 密码: admin
echo 4. 查找攻击类型为 "DosFam" 的记录
echo 5. 检查威胁级别是否为 "高危" 或 "中危"
echo.
echo 预期结果:
echo - 应该看到大量 "DosFam" 类型的攻击记录
echo - 威胁级别应该显示为 "高危"
echo - 源IP地址应该是 127.0.0.1
echo - 时间戳应该是刚才的测试时间
echo.
echo 按任意键打开管理后台查看结果...
pause >nul

start http://127.0.0.1:8000/admin/main/trafficlog/
