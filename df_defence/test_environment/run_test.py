#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Attack-Defense Environment Test Startup Script
攻防环境测试启动脚本
"""

import os
import sys
import time
import subprocess
import threading
import signal
import requests
from datetime import datetime

class TestEnvironment:
    def __init__(self):
        self.django_process = None
        self.attack_process = None
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def start_django_server(self):
        """Start Django server / 启动Django服务器"""
        print("Starting Django server...")
        try:
            os.chdir(self.base_dir)
            self.django_process = subprocess.Popen(
                [sys.executable, "manage.py", "runserver", "127.0.0.1:8000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Wait for server to start / 等待服务器启动
            for i in range(30):
                try:
                    response = requests.get("http://127.0.0.1:8000/", timeout=2)
                    if response.status_code in [200, 302, 404]:
                        print("✓ Django server started successfully")
                        return True
                except:
                    time.sleep(1)

            print("✗ Django server failed to start")
            return False

        except Exception as e:
            print(f"Error starting Django server: {e}")
            return False

    def wait_for_user_ready(self):
        """Wait for user confirmation / 等待用户确认准备就绪"""
        print("\n" + "="*60)
        print("Test environment is ready!")
        print("Please ensure the following steps are completed:")
        print("1. Django server is running (http://127.0.0.1:8000)")
        print("2. Logged into admin backend (http://127.0.0.1:8000/admin)")
        print("3. Can view traffic logs and detection results")
        print("="*60)

        input("Press Enter to start attack testing...")

    def run_attack_simulation(self):
        """Run attack simulation / 运行攻击模拟"""
        print("\nStarting attack simulation...")

        attack_script = os.path.join(os.path.dirname(__file__), "attack_simulator.py")

        try:
            # Run attack simulator / 运行攻击模拟器
            self.attack_process = subprocess.Popen([
                sys.executable, attack_script,
                "--target", "127.0.0.1",
                "--port", "8000",
                "--attack", "all",
                "--normal"
            ])

            print("✓ Attack simulator started")
            return True

        except Exception as e:
            print(f"Error starting attack simulator: {e}")
            return False

    def monitor_system(self):
        """Monitor system status / 监控系统状态"""
        print("\nStarting system monitoring...")

        start_time = time.time()

        while True:
            try:
                # Check Django server status / 检查Django服务器状态
                response = requests.get("http://127.0.0.1:8000/admin/", timeout=5)
                server_status = "Running" if response.status_code in [200, 302] else "Error"

                # Check attack process status / 检查攻击进程状态
                if self.attack_process:
                    attack_status = "Running" if self.attack_process.poll() is None else "Completed"
                else:
                    attack_status = "Not Started"

                # Display status / 显示状态
                elapsed = int(time.time() - start_time)
                print(f"\r[{elapsed:03d}s] Django: {server_status} | Attack Simulation: {attack_status}", end="", flush=True)

                # Exit monitoring if attack is completed / 如果攻击完成，退出监控
                if self.attack_process and self.attack_process.poll() is not None:
                    print("\nAttack simulation completed!")
                    break

                time.sleep(2)

            except KeyboardInterrupt:
                print("\nUser interrupted monitoring")
                break
            except Exception as e:
                print(f"\nMonitoring error: {e}")
                time.sleep(5)

    def show_results(self):
        """Display test results / 显示测试结果"""
        print("\n" + "="*60)
        print("Test completed! Please check the following:")
        print("="*60)
        print("1. Django admin backend: http://127.0.0.1:8000/admin/")
        print("   - Username: admin")
        print("   - Password: admin")
        print()
        print("2. View detection results:")
        print("   - Traffic logs: http://127.0.0.1:8000/admin/main/trafficlog/")
        print("   - IP rules: http://127.0.0.1:8000/admin/main/ipaddressrule/")
        print("   - Tuning models: http://127.0.0.1:8000/admin/main/tuningmodels/")
        print()
        print("3. Main application interface: http://127.0.0.1:8000/")
        print()
        print("4. Check detection logs in terminal output")
        print("="*60)

    def cleanup(self):
        """Clean up resources / 清理资源"""
        print("\nCleaning up test environment...")

        if self.attack_process:
            try:
                self.attack_process.terminate()
                self.attack_process.wait(timeout=5)
                print("✓ Attack simulator stopped")
            except:
                try:
                    self.attack_process.kill()
                except:
                    pass

        if self.django_process:
            try:
                self.django_process.terminate()
                self.django_process.wait(timeout=5)
                print("✓ Django server stopped")
            except:
                try:
                    self.django_process.kill()
                except:
                    pass

    def run_full_test(self):
        """Run complete test / 运行完整测试"""
        try:
            print("Deep Learning Network Traffic Anomaly Detection System - Attack-Defense Environment Test")
            print("="*60)
            print(f"Test start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)

            # 1. Start Django server / 启动Django服务器
            if not self.start_django_server():
                return False

            # 2. Wait for user preparation / 等待用户准备
            self.wait_for_user_ready()

            # 3. Start attack simulation / 启动攻击模拟
            if not self.run_attack_simulation():
                return False

            # 4. Monitor system / 监控系统
            self.monitor_system()

            # 5. Display results / 显示结果
            self.show_results()

            return True

        except KeyboardInterrupt:
            print("\nUser interrupted test")
            return False
        except Exception as e:
            print(f"Error during test: {e}")
            return False
        finally:
            self.cleanup()

def signal_handler(signum, frame):
    """Signal handler / 信号处理器"""
    print("\nReceived interrupt signal, cleaning up...")
    sys.exit(0)

def check_requirements():
    """Check runtime requirements / 检查运行要求"""
    print("Checking runtime environment...")

    # Check Python version / 检查Python版本
    if sys.version_info < (3, 6):
        print("✗ Python 3.6 or higher is required")
        return False

    # Check required modules / 检查必要的模块
    required_modules = ['django', 'requests', 'scapy', 'torch', 'numpy', 'pandas']
    missing_modules = []

    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print(f"✗ Missing required modules: {', '.join(missing_modules)}")
        print("Please run: pip install " + " ".join(missing_modules))
        return False

    print("✓ Runtime environment check passed")
    return True

def main():
    # Set signal handling / 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Check requirements / 检查运行要求
    if not check_requirements():
        sys.exit(1)

    # Create test environment / 创建测试环境
    test_env = TestEnvironment()

    # Run test / 运行测试
    success = test_env.run_full_test()

    if success:
        print("\nTest completed successfully!")
        sys.exit(0)
    else:
        print("\nTest failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
