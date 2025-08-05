#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local DDoS Attack Test Script
Run in Django project directory, ensure correct path
本地DDoS攻击测试脚本 - 在Django项目目录中运行，确保路径正确
"""

import urllib.request
import urllib.error
import time
import threading
import random
import os
import django

# Set Django environment / 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dl_ids.settings')
django.setup()

from main.models import TrafficLog

def test_ddos_detection():
    """Test DDoS detection functionality / 测试DDoS检测功能"""
    print("=" * 70)
    print("Local DDoS Attack Test")
    print("=" * 70)

    target_url = "http://127.0.0.1:8000"

    # Clear previous records / 清空之前的记录
    initial_count = TrafficLog.objects.count()
    print(f"Database records before test: {initial_count}")

    print("\nStarting DDoS attack test...")

    # 1. Send normal requests / 发送正常请求
    print("\n1. Sending normal requests...")
    try:
        req = urllib.request.Request(f"{target_url}/")
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"Normal request: {response.getcode()}")
    except Exception as e:
        print(f"Normal request failed: {e}")

    time.sleep(2)

    # 2. Send DDoS attack requests / 发送DDoS攻击请求
    print("\n2. Sending DDoS attack requests...")

    def ddos_attack_worker():
        """DDoS attack worker thread / DDoS攻击工作线程"""
        for i in range(20):  # Each thread sends 20 requests / 每个线程发送20个请求
            try:
                req = urllib.request.Request(f"{target_url}/")
                req.add_header('User-Agent', 'DDoSBot/1.0 (Flood Attack)')
                req.add_header('X-Attack-Type', 'HTTP-Flood')
                req.add_header('X-Forwarded-For', f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}")

                with urllib.request.urlopen(req, timeout=3) as response:
                    pass  # No need to process response / 不需要处理响应

                time.sleep(0.1)  # Brief delay / 短暂延迟

            except urllib.error.HTTPError as e:
                if e.code == 429:  # Blocked requests also count as success / 被阻止的请求也算成功
                    print("Request blocked by DDoS protection - Detection successful!")
                pass
            except Exception as e:
                pass  # Ignore other errors / 忽略其他错误

    # Start multiple attack threads / 启动多个攻击线程
    threads = []
    for i in range(5):  # 5 threads / 5个线程
        t = threading.Thread(target=ddos_attack_worker)
        t.start()
        threads.append(t)
        print(f"Started attack thread {i+1}")

    # Wait for all threads to complete / 等待所有线程完成
    for t in threads:
        t.join()

    print("DDoS attack completed")

    # 3. Wait for middleware processing / 等待中间件处理
    print("\n3. Waiting for middleware processing...")
    time.sleep(5)

    # 4. Check results / 检查结果
    print("\n4. Checking detection results...")
    final_count = TrafficLog.objects.count()
    new_records = final_count - initial_count

    print(f"Database records after test: {final_count}")
    print(f"New records: {new_records}")

    if new_records > 0:
        print("✅ DDoS detection successful!")

        # Display detected records / 显示检测到的记录
        recent_logs = TrafficLog.objects.all().order_by('-created_at')[:new_records]

        ddos_count = 0
        normal_count = 0

        print("\nDetected attack records:")
        for i, log in enumerate(recent_logs):
            time_str = log.created_at.strftime("%H:%M:%S")
            print(f"  {i+1:2d}. {time_str} - {log.src_ip} - {log.attack_type} - {log.threat_level}")

            if log.attack_type == 'DosFam':
                ddos_count += 1
            elif log.attack_type == 'BENIGN':
                normal_count += 1

        print(f"\nStatistics:")
        print(f"  DDoS attack records: {ddos_count}")
        print(f"  Normal traffic records: {normal_count}")

        if ddos_count > 0:
            print(f"\n🎯 Test Conclusion:")
            print(f"   ✅ Deep learning DDoS detection system is working properly!")
            print(f"   ✅ Successfully identified {ddos_count} DDoS attacks")
            print(f"   ✅ Detection rate: {(ddos_count / new_records) * 100:.1f}%")
        else:
            print(f"\n⚠️  Traffic detected but not identified as DDoS attack")
            print(f"   Detection threshold may need adjustment")

    else:
        print("❌ No traffic records detected")
        print("Possible issues:")
        print("1. DDoS middleware not properly loaded")
        print("2. Requests did not reach Django server")
        print("3. Database connection issues")

        # Test basic connection / 测试基本连接
        print("\nTesting basic connection...")
        try:
            req = urllib.request.Request(f"{target_url}/")
            with urllib.request.urlopen(req, timeout=5) as response:
                print(f"✅ Basic connection normal: {response.getcode()}")
        except Exception as e:
            print(f"❌ Basic connection failed: {e}")

def main():
    print("Ensure Django server is running...")
    print("URL: http://127.0.0.1:8000")
    print("Press Enter to start test...")
    input()

    test_ddos_detection()

    print("\n" + "=" * 70)
    print("Test completed!")
    print("View results: http://127.0.0.1:8000/traffic-log/")
    print("=" * 70)

if __name__ == "__main__":
    main()
