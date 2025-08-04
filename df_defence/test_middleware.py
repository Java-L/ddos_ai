#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试DDoS中间件是否正常工作
"""

import os
import django
import urllib.request
import urllib.error
import time

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dl_ids.settings')
django.setup()

from main.models import TrafficLog

def test_middleware():
    print("=" * 60)
    print("测试DDoS检测中间件")
    print("=" * 60)
    
    # 清空之前的记录
    initial_count = TrafficLog.objects.count()
    print(f"测试前数据库记录数: {initial_count}")
    
    print("\n发送测试请求...")
    
    # 发送几个测试请求
    test_requests = [
        {
            'url': 'http://127.0.0.1:8000/',
            'headers': {'User-Agent': 'DDoSBot/1.0 (Test Attack)', 'X-Attack-Type': 'HTTP-Flood'}
        },
        {
            'url': 'http://127.0.0.1:8000/',
            'headers': {'User-Agent': 'Mozilla/5.0 (Normal Browser)'}
        },
        {
            'url': 'http://127.0.0.1:8000/traffic-log/',
            'headers': {'User-Agent': 'DDoSBot/1.0 (Flood Attack)'}
        }
    ]
    
    success_count = 0
    for i, req_data in enumerate(test_requests):
        try:
            req = urllib.request.Request(req_data['url'])
            for key, value in req_data['headers'].items():
                req.add_header(key, value)
            
            with urllib.request.urlopen(req, timeout=5) as response:
                print(f"请求 {i+1}: {response.getcode()} - {req_data['headers'].get('User-Agent', 'Unknown')}")
                success_count += 1
                
        except urllib.error.HTTPError as e:
            print(f"请求 {i+1}: HTTP错误 {e.code} - {req_data['headers'].get('User-Agent', 'Unknown')}")
            success_count += 1  # HTTP错误也算到达了服务器
        except Exception as e:
            print(f"请求 {i+1}: 失败 - {e}")
        
        time.sleep(1)  # 间隔1秒
    
    print(f"\n成功发送 {success_count}/{len(test_requests)} 个请求")
    
    # 等待一下让中间件处理
    print("等待3秒让中间件处理...")
    time.sleep(3)
    
    # 检查数据库记录
    final_count = TrafficLog.objects.count()
    new_records = final_count - initial_count
    
    print(f"\n测试后数据库记录数: {final_count}")
    print(f"新增记录数: {new_records}")
    
    if new_records > 0:
        print("✅ DDoS中间件工作正常!")
        
        # 显示新记录
        recent_logs = TrafficLog.objects.all().order_by('-created_at')[:new_records]
        print("\n新增的记录:")
        for i, log in enumerate(recent_logs):
            print(f"  {i+1}. {log.src_ip} -> {log.dst_ip} - {log.attack_type} - {log.threat_level}")
            
    else:
        print("❌ DDoS中间件未记录任何数据")
        print("可能的问题:")
        print("1. 中间件未正确加载")
        print("2. 数据库连接问题")
        print("3. 中间件代码有错误")

if __name__ == "__main__":
    test_middleware()
