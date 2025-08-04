#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
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
        """启动Django服务器"""
        print("启动Django服务器...")
        try:
            os.chdir(self.base_dir)
            self.django_process = subprocess.Popen(
                [sys.executable, "manage.py", "runserver", "127.0.0.1:8000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 等待服务器启动
            for i in range(30):
                try:
                    response = requests.get("http://127.0.0.1:8000/", timeout=2)
                    if response.status_code in [200, 302, 404]:
                        print("✓ Django服务器启动成功")
                        return True
                except:
                    time.sleep(1)
                    
            print("✗ Django服务器启动失败")
            return False
            
        except Exception as e:
            print(f"启动Django服务器时出错: {e}")
            return False
    
    def wait_for_user_ready(self):
        """等待用户确认准备就绪"""
        print("\n" + "="*60)
        print("测试环境准备就绪！")
        print("请确保以下步骤已完成：")
        print("1. Django服务器正在运行 (http://127.0.0.1:8000)")
        print("2. 已登录管理后台 (http://127.0.0.1:8000/admin)")
        print("3. 可以查看流量日志和检测结果")
        print("="*60)
        
        input("按回车键开始攻击测试...")
    
    def run_attack_simulation(self):
        """运行攻击模拟"""
        print("\n开始攻击模拟...")
        
        attack_script = os.path.join(os.path.dirname(__file__), "attack_simulator.py")
        
        try:
            # 运行攻击模拟器
            self.attack_process = subprocess.Popen([
                sys.executable, attack_script,
                "--target", "127.0.0.1",
                "--port", "8000", 
                "--attack", "all",
                "--normal"
            ])
            
            print("✓ 攻击模拟器已启动")
            return True
            
        except Exception as e:
            print(f"启动攻击模拟器时出错: {e}")
            return False
    
    def monitor_system(self):
        """监控系统状态"""
        print("\n开始监控系统...")
        
        start_time = time.time()
        
        while True:
            try:
                # 检查Django服务器状态
                response = requests.get("http://127.0.0.1:8000/admin/", timeout=5)
                server_status = "运行中" if response.status_code in [200, 302] else "异常"
                
                # 检查攻击进程状态
                if self.attack_process:
                    attack_status = "运行中" if self.attack_process.poll() is None else "已完成"
                else:
                    attack_status = "未启动"
                
                # 显示状态
                elapsed = int(time.time() - start_time)
                print(f"\r[{elapsed:03d}s] Django: {server_status} | 攻击模拟: {attack_status}", end="", flush=True)
                
                # 如果攻击完成，退出监控
                if self.attack_process and self.attack_process.poll() is not None:
                    print("\n攻击模拟完成！")
                    break
                    
                time.sleep(2)
                
            except KeyboardInterrupt:
                print("\n用户中断监控")
                break
            except Exception as e:
                print(f"\n监控出错: {e}")
                time.sleep(5)
    
    def show_results(self):
        """显示测试结果"""
        print("\n" + "="*60)
        print("测试完成！请查看以下内容：")
        print("="*60)
        print("1. Django管理后台: http://127.0.0.1:8000/admin/")
        print("   - 用户名: admin")
        print("   - 密码: admin")
        print()
        print("2. 查看检测结果：")
        print("   - 流量日志: http://127.0.0.1:8000/admin/main/trafficlog/")
        print("   - IP规则: http://127.0.0.1:8000/admin/main/ipaddressrule/")
        print("   - 调优模型: http://127.0.0.1:8000/admin/main/tuningmodels/")
        print()
        print("3. 主应用界面: http://127.0.0.1:8000/")
        print()
        print("4. 检查终端输出中的检测日志")
        print("="*60)
    
    def cleanup(self):
        """清理资源"""
        print("\n清理测试环境...")
        
        if self.attack_process:
            try:
                self.attack_process.terminate()
                self.attack_process.wait(timeout=5)
                print("✓ 攻击模拟器已停止")
            except:
                try:
                    self.attack_process.kill()
                except:
                    pass
        
        if self.django_process:
            try:
                self.django_process.terminate()
                self.django_process.wait(timeout=5)
                print("✓ Django服务器已停止")
            except:
                try:
                    self.django_process.kill()
                except:
                    pass
    
    def run_full_test(self):
        """运行完整测试"""
        try:
            print("深度学习网络流量异常检测系统 - 攻防环境测试")
            print("="*60)
            print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)
            
            # 1. 启动Django服务器
            if not self.start_django_server():
                return False
            
            # 2. 等待用户准备
            self.wait_for_user_ready()
            
            # 3. 启动攻击模拟
            if not self.run_attack_simulation():
                return False
            
            # 4. 监控系统
            self.monitor_system()
            
            # 5. 显示结果
            self.show_results()
            
            return True
            
        except KeyboardInterrupt:
            print("\n用户中断测试")
            return False
        except Exception as e:
            print(f"测试过程中出错: {e}")
            return False
        finally:
            self.cleanup()

def signal_handler(signum, frame):
    """信号处理器"""
    print("\n收到中断信号，正在清理...")
    sys.exit(0)

def check_requirements():
    """检查运行要求"""
    print("检查运行环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 6):
        print("✗ 需要Python 3.6或更高版本")
        return False
    
    # 检查必要的模块
    required_modules = ['django', 'requests', 'scapy', 'torch', 'numpy', 'pandas']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"✗ 缺少必要模块: {', '.join(missing_modules)}")
        print("请运行: pip install " + " ".join(missing_modules))
        return False
    
    print("✓ 运行环境检查通过")
    return True

def main():
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 检查运行要求
    if not check_requirements():
        sys.exit(1)
    
    # 创建测试环境
    test_env = TestEnvironment()
    
    # 运行测试
    success = test_env.run_full_test()
    
    if success:
        print("\n测试成功完成！")
        sys.exit(0)
    else:
        print("\n测试失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
