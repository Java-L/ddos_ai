#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础网络测试脚本
使用Python标准库进行简单的网络连接测试
"""

import socket
import time
import random
import threading
import urllib.request
import urllib.parse
import urllib.error

class BasicNetworkTester:
    def __init__(self, target_ip="127.0.0.1", target_port=8000):
        self.target_ip = target_ip
        self.target_port = target_port
        
    def test_connection(self):
        """测试基本连接"""
        print(f"测试连接到 {self.target_ip}:{self.target_port}")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.target_ip, self.target_port))
            sock.close()
            
            if result == 0:
                print("✓ 连接成功")
                return True
            else:
                print("✗ 连接失败")
                return False
        except Exception as e:
            print(f"✗ 连接错误: {e}")
            return False
    
    def send_http_requests(self, count=10):
        """发送HTTP请求"""
        print(f"发送 {count} 个HTTP请求...")
        
        success_count = 0
        
        for i in range(count):
            try:
                url = f"http://{self.target_ip}:{self.target_port}/"
                
                # 构造请求
                req = urllib.request.Request(url)
                req.add_header('User-Agent', f'TestBot/1.0 Request-{i+1}')
                
                # 发送请求
                with urllib.request.urlopen(req, timeout=5) as response:
                    status_code = response.getcode()
                    success_count += 1
                    print(f"请求 #{i+1}: 状态码 {status_code}")
                
                time.sleep(random.uniform(0.5, 2.0))
                
            except urllib.error.HTTPError as e:
                print(f"请求 #{i+1}: HTTP错误 {e.code}")
            except urllib.error.URLError as e:
                print(f"请求 #{i+1}: URL错误 {e.reason}")
            except Exception as e:
                print(f"请求 #{i+1}: 其他错误 {e}")
        
        print(f"完成，成功 {success_count}/{count} 个请求")
        return success_count
    
    def simulate_malicious_requests(self, count=5):
        """模拟恶意请求"""
        print(f"模拟 {count} 个恶意请求...")
        
        malicious_payloads = [
            "' OR '1'='1",
            "<script>alert('test')</script>",
            "../../../etc/passwd",
            "admin' --",
            "SELECT * FROM users"
        ]
        
        for i in range(count):
            try:
                payload = random.choice(malicious_payloads)
                # 编码恶意载荷
                encoded_payload = urllib.parse.quote(payload)
                url = f"http://{self.target_ip}:{self.target_port}/admin/?q={encoded_payload}"
                
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'MaliciousBot/1.0')
                req.add_header('X-Attack-Type', 'SQL-Injection')
                
                with urllib.request.urlopen(req, timeout=5) as response:
                    status_code = response.getcode()
                    print(f"恶意请求 #{i+1}: 状态码 {status_code} - 载荷: {payload[:20]}...")
                
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"恶意请求 #{i+1}: 错误 {e}")
    
    def port_scan_simulation(self, start_port=8000, end_port=8010):
        """模拟端口扫描"""
        print(f"模拟端口扫描 {self.target_ip}:{start_port}-{end_port}")
        
        open_ports = []
        
        for port in range(start_port, end_port + 1):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((self.target_ip, port))
                
                if result == 0:
                    print(f"端口 {port}: 开放")
                    open_ports.append(port)
                else:
                    print(f"端口 {port}: 关闭")
                
                sock.close()
                time.sleep(0.5)
                
            except Exception as e:
                print(f"端口 {port}: 扫描错误 {e}")
        
        print(f"扫描完成，发现 {len(open_ports)} 个开放端口: {open_ports}")
        return open_ports
    
    def flood_simulation(self, duration=10):
        """模拟流量洪水攻击"""
        print(f"模拟流量洪水攻击，持续 {duration} 秒")
        
        start_time = time.time()
        request_count = 0
        
        def send_flood_requests():
            nonlocal request_count
            while (time.time() - start_time) < duration:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    sock.connect((self.target_ip, self.target_port))
                    
                    # 发送简单的HTTP请求
                    request = f"GET / HTTP/1.1\r\nHost: {self.target_ip}\r\nUser-Agent: FloodBot\r\n\r\n"
                    sock.send(request.encode())
                    sock.close()
                    
                    request_count += 1
                    
                except:
                    pass
                
                time.sleep(0.1)
        
        # 启动多个线程
        threads = []
        for i in range(3):
            t = threading.Thread(target=send_flood_requests)
            t.start()
            threads.append(t)
        
        time.sleep(duration)
        
        for t in threads:
            t.join()
        
        print(f"洪水攻击完成，共发送 {request_count} 个连接")

def main():
    print("=" * 60)
    print("基础网络测试工具")
    print("=" * 60)
    
    target_ip = "127.0.0.1"
    target_port = 8000
    
    tester = BasicNetworkTester(target_ip, target_port)
    
    print(f"目标: {target_ip}:{target_port}")
    print()
    
    # 1. 测试基本连接
    if not tester.test_connection():
        print("无法连接到目标，请确保Django服务器正在运行")
        return
    
    print()
    
    # 2. 发送正常请求
    print("步骤1: 发送正常HTTP请求")
    tester.send_http_requests(5)
    
    print()
    time.sleep(2)
    
    # 3. 模拟恶意请求
    print("步骤2: 模拟恶意请求")
    tester.simulate_malicious_requests(3)
    
    print()
    time.sleep(2)
    
    # 4. 端口扫描
    print("步骤3: 模拟端口扫描")
    tester.port_scan_simulation(8000, 8005)
    
    print()
    time.sleep(2)
    
    # 5. 流量洪水
    print("步骤4: 模拟流量洪水攻击")
    tester.flood_simulation(8)
    
    print()
    print("=" * 60)
    print("测试完成！")
    print("请检查Django管理后台查看检测结果:")
    print(f"http://{target_ip}:{target_port}/admin/main/trafficlog/")
    print("用户名: admin, 密码: admin")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户中断测试")
    except Exception as e:
        print(f"测试出错: {e}")
