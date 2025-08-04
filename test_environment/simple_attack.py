#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的网络攻击模拟器
用于测试深度学习网络流量异常检测系统
"""

import time
import random
import requests
import threading
import sys

class SimpleAttackSimulator:
    def __init__(self, target_ip="127.0.0.1", target_port=8000):
        self.target_ip = target_ip
        self.target_port = target_port
        
    def web_attack(self, duration=20):
        """模拟Web攻击"""
        print(f"[Web攻击] 开始对 http://{self.target_ip}:{self.target_port} 进行Web攻击，持续{duration}秒")
        
        # 常见的Web攻击载荷
        payloads = [
            "' OR '1'='1",  # SQL注入
            "<script>alert('XSS')</script>",  # XSS
            "../../../etc/passwd",  # 路径遍历
            "admin' --",  # SQL注入
            "<img src=x onerror=alert(1)>",  # XSS
            "'; DROP TABLE users; --",  # SQL注入
        ]
        
        start_time = time.time()
        request_count = 0
        
        while (time.time() - start_time) < duration:
            try:
                # 随机选择攻击载荷
                payload = random.choice(payloads)
                
                # 构造恶意请求
                urls = [
                    f"http://{self.target_ip}:{self.target_port}/admin/",
                    f"http://{self.target_ip}:{self.target_port}/admin/login/",
                    f"http://{self.target_ip}:{self.target_port}/admin/main/trafficlog/?q={payload}",
                    f"http://{self.target_ip}:{self.target_port}/search?q={payload}",
                ]
                
                url = random.choice(urls)
                
                # 发送恶意请求
                headers = {
                    'User-Agent': 'AttackBot/1.0 (Malicious Scanner)',
                    'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                }
                
                response = requests.get(url, headers=headers, timeout=5)
                request_count += 1
                print(f"恶意请求 #{request_count}: 状态码 {response.status_code} - {payload[:30]}...")
                
            except Exception as e:
                print(f"请求错误: {e}")
                
            time.sleep(random.uniform(0.5, 2.0))
            
        print(f"[Web攻击] 攻击结束，共发送 {request_count} 个恶意请求")
    
    def brute_force_attack(self, duration=15):
        """模拟暴力破解攻击"""
        print(f"[暴力破解] 开始暴力破解攻击，持续{duration}秒")
        
        usernames = ["admin", "root", "user", "test", "guest"]
        passwords = ["123456", "password", "admin", "root", "test"]
        
        start_time = time.time()
        attempt_count = 0
        
        while (time.time() - start_time) < duration:
            try:
                username = random.choice(usernames)
                password = random.choice(passwords)
                
                # 模拟登录尝试
                login_data = {
                    'username': username,
                    'password': password,
                    'next': '/admin/'
                }
                
                headers = {
                    'User-Agent': 'BruteForcer/1.0',
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
                
                response = requests.post(
                    f"http://{self.target_ip}:{self.target_port}/admin/login/",
                    data=login_data,
                    headers=headers,
                    timeout=5,
                    allow_redirects=False
                )
                
                attempt_count += 1
                print(f"暴力破解尝试 #{attempt_count}: {username}:{password} - 状态码: {response.status_code}")
                
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"暴力破解错误: {e}")
                time.sleep(1)
        
        print(f"[暴力破解] 攻击结束，共尝试 {attempt_count} 次")
    
    def dos_simulation(self, duration=10):
        """模拟DoS攻击（简化版）"""
        print(f"[DoS模拟] 开始DoS攻击模拟，持续{duration}秒")
        
        start_time = time.time()
        request_count = 0
        
        def send_requests():
            nonlocal request_count
            while (time.time() - start_time) < duration:
                try:
                    # 快速发送大量请求
                    for _ in range(5):
                        response = requests.get(
                            f"http://{self.target_ip}:{self.target_port}/",
                            timeout=2,
                            headers={'User-Agent': 'DoSBot/1.0'}
                        )
                        request_count += 1
                    time.sleep(0.1)
                except:
                    pass
        
        # 启动多个线程
        threads = []
        for i in range(3):
            t = threading.Thread(target=send_requests)
            t.start()
            threads.append(t)
        
        time.sleep(duration)
        
        for t in threads:
            t.join()
        
        print(f"[DoS模拟] 攻击结束，共发送 {request_count} 个请求")

def generate_normal_traffic(target_ip="127.0.0.1", target_port=8000, duration=30):
    """生成正常流量"""
    print(f"[正常流量] 开始生成正常流量，持续{duration}秒")
    
    start_time = time.time()
    request_count = 0
    
    while (time.time() - start_time) < duration:
        try:
            # 模拟正常的HTTP请求
            normal_urls = [
                f"http://{target_ip}:{target_port}/",
                f"http://{target_ip}:{target_port}/admin/",
                f"http://{target_ip}:{target_port}/static/admin/css/base.css",
                f"http://{target_ip}:{target_port}/admin/main/trafficlog/",
            ]
            
            url = random.choice(normal_urls)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            request_count += 1
            print(f"正常请求 #{request_count}: {url.split('/')[-1] or 'index'} - 状态码: {response.status_code}")
            
            # 正常间隔
            time.sleep(random.uniform(3, 8))
            
        except Exception as e:
            print(f"正常流量生成错误: {e}")
            time.sleep(1)
    
    print(f"[正常流量] 生成结束，共发送 {request_count} 个正常请求")

def main():
    print("=" * 60)
    print("简化网络攻击模拟器")
    print("=" * 60)
    
    target_ip = "127.0.0.1"
    target_port = 8000
    
    simulator = SimpleAttackSimulator(target_ip, target_port)
    
    print(f"目标: {target_ip}:{target_port}")
    print("开始攻击序列...")
    print()
    
    # 启动正常流量生成（后台）
    normal_thread = threading.Thread(
        target=generate_normal_traffic, 
        args=(target_ip, target_port, 60)
    )
    normal_thread.start()
    
    # 依次执行各种攻击
    time.sleep(2)
    simulator.web_attack(15)
    
    time.sleep(3)
    simulator.brute_force_attack(12)
    
    time.sleep(3)
    simulator.dos_simulation(8)
    
    # 等待正常流量线程结束
    normal_thread.join()
    
    print("\n" + "=" * 60)
    print("攻击模拟完成！")
    print("请检查Django管理后台查看检测结果:")
    print(f"http://{target_ip}:{target_port}/admin/main/trafficlog/")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户中断攻击模拟")
    except Exception as e:
        print(f"攻击模拟出错: {e}")
