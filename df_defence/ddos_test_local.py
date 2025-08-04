#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地DDoS攻击测试脚本
在Django项目目录中运行，确保路径正确
"""

import urllib.request
import urllib.error
import time
import threading
import random
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dl_ids.settings')
django.setup()

from main.models import TrafficLog

def test_ddos_detection():
    """测试DDoS检测功能"""
    print("=" * 70)
    print("本地DDoS攻击测试")
    print("=" * 70)
    
    target_url = "http://127.0.0.1:8000"
    
    # 清空之前的记录
    initial_count = TrafficLog.objects.count()
    print(f"测试前数据库记录数: {initial_count}")
    
    print("\n开始DDoS攻击测试...")
    
    # 1. 发送正常请求
    print("\n1. 发送正常请求...")
    try:
        req = urllib.request.Request(f"{target_url}/")
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"正常请求: {response.getcode()}")
    except Exception as e:
        print(f"正常请求失败: {e}")
    
    time.sleep(2)
    
    # 2. 发送DDoS攻击请求
    print("\n2. 发送DDoS攻击请求...")
    
    def ddos_attack_worker():
        """DDoS攻击工作线程"""
        for i in range(20):  # 每个线程发送20个请求
            try:
                req = urllib.request.Request(f"{target_url}/")
                req.add_header('User-Agent', 'DDoSBot/1.0 (Flood Attack)')
                req.add_header('X-Attack-Type', 'HTTP-Flood')
                req.add_header('X-Forwarded-For', f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}")
                
                with urllib.request.urlopen(req, timeout=3) as response:
                    pass  # 不需要处理响应
                
                time.sleep(0.1)  # 短暂延迟
                
            except urllib.error.HTTPError as e:
                if e.code == 429:  # 被阻止的请求也算成功
                    print("请求被DDoS保护阻止 - 检测成功!")
                pass
            except Exception as e:
                pass  # 忽略其他错误
    
    # 启动多个攻击线程
    threads = []
    for i in range(5):  # 5个线程
        t = threading.Thread(target=ddos_attack_worker)
        t.start()
        threads.append(t)
        print(f"启动攻击线程 {i+1}")
    
    # 等待所有线程完成
    for t in threads:
        t.join()
    
    print("DDoS攻击完成")
    
    # 3. 等待中间件处理
    print("\n3. 等待中间件处理...")
    time.sleep(5)
    
    # 4. 检查结果
    print("\n4. 检查检测结果...")
    final_count = TrafficLog.objects.count()
    new_records = final_count - initial_count
    
    print(f"测试后数据库记录数: {final_count}")
    print(f"新增记录数: {new_records}")
    
    if new_records > 0:
        print("✅ DDoS检测成功!")
        
        # 显示检测到的记录
        recent_logs = TrafficLog.objects.all().order_by('-created_at')[:new_records]
        
        ddos_count = 0
        normal_count = 0
        
        print("\n检测到的攻击记录:")
        for i, log in enumerate(recent_logs):
            time_str = log.created_at.strftime("%H:%M:%S")
            print(f"  {i+1:2d}. {time_str} - {log.src_ip} - {log.attack_type} - {log.threat_level}")
            
            if log.attack_type == 'DosFam':
                ddos_count += 1
            elif log.attack_type == 'BENIGN':
                normal_count += 1
        
        print(f"\n统计结果:")
        print(f"  DDoS攻击记录: {ddos_count}")
        print(f"  正常流量记录: {normal_count}")
        
        if ddos_count > 0:
            print(f"\n🎯 测试结论:")
            print(f"   ✅ 深度学习DDoS检测系统工作正常!")
            print(f"   ✅ 成功识别了 {ddos_count} 次 DDoS 攻击")
            print(f"   ✅ 检测率: {(ddos_count / new_records) * 100:.1f}%")
        else:
            print(f"\n⚠️  检测到流量但未识别为DDoS攻击")
            print(f"   可能需要调整检测阈值")
    
    else:
        print("❌ 未检测到任何流量记录")
        print("可能的问题:")
        print("1. DDoS中间件未正确加载")
        print("2. 请求没有到达Django服务器")
        print("3. 数据库连接问题")
        
        # 测试基本连接
        print("\n测试基本连接...")
        try:
            req = urllib.request.Request(f"{target_url}/")
            with urllib.request.urlopen(req, timeout=5) as response:
                print(f"✅ 基本连接正常: {response.getcode()}")
        except Exception as e:
            print(f"❌ 基本连接失败: {e}")

def main():
    print("确保Django服务器正在运行...")
    print("URL: http://127.0.0.1:8000")
    print("按Enter键开始测试...")
    input()
    
    test_ddos_detection()
    
    print("\n" + "=" * 70)
    print("测试完成!")
    print("查看结果: http://127.0.0.1:8000/traffic-log/")
    print("=" * 70)

if __name__ == "__main__":
    main()
