#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试DDoS中间件
"""

import os
import django
from django.test import RequestFactory

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dl_ids.settings')
django.setup()

from main.ddos_middleware import DDoSDetectionMiddleware
from main.models import TrafficLog

def test_middleware_directly():
    print("=" * 60)
    print("直接测试DDoS中间件")
    print("=" * 60)
    
    # 创建请求工厂
    factory = RequestFactory()
    
    # 创建中间件实例
    def dummy_get_response(request):
        from django.http import HttpResponse
        return HttpResponse("OK")
    
    middleware = DDoSDetectionMiddleware(dummy_get_response)
    
    print("✅ 中间件创建成功")
    
    # 清空数据库
    initial_count = TrafficLog.objects.count()
    print(f"测试前数据库记录数: {initial_count}")
    
    # 创建测试请求
    print("\n创建测试请求...")
    
    # 1. 正常请求
    request1 = factory.get('/')
    request1.META['REMOTE_ADDR'] = '192.168.1.100'
    request1.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Normal Browser)'
    
    print("发送正常请求...")
    response1 = middleware(request1)
    print(f"正常请求响应: {response1.status_code}")
    
    # 2. DDoS攻击请求
    request2 = factory.get('/')
    request2.META['REMOTE_ADDR'] = '192.168.1.101'
    request2.META['HTTP_USER_AGENT'] = 'DDoSBot/1.0 (Attack)'
    request2.META['HTTP_X_ATTACK_TYPE'] = 'HTTP-Flood'
    
    print("发送DDoS攻击请求...")
    response2 = middleware(request2)
    print(f"DDoS请求响应: {response2.status_code}")
    
    # 3. 多个快速请求（模拟DDoS）
    print("发送多个快速请求...")
    for i in range(10):
        request = factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.102'
        request.META['HTTP_USER_AGENT'] = 'DDoSBot/2.0 (Flood)'
        response = middleware(request)
        print(f"  请求 {i+1}: {response.status_code}")
    
    # 等待异步线程完成
    print("\n等待异步线程完成...")
    import time
    time.sleep(3)

    # 检查结果
    print("检查结果...")
    final_count = TrafficLog.objects.count()
    new_records = final_count - initial_count
    
    print(f"测试后数据库记录数: {final_count}")
    print(f"新增记录数: {new_records}")
    
    if new_records > 0:
        print("✅ 中间件工作正常!")
        
        # 显示记录
        recent_logs = TrafficLog.objects.all().order_by('-create_time')[:new_records]
        
        print("\n检测到的记录:")
        for i, log in enumerate(recent_logs):
            print(f"  {i+1}. {log.src_ip} - {log.attack_type} - {log.threat}")
            
    else:
        print("❌ 中间件未记录任何数据")

if __name__ == "__main__":
    test_middleware_directly()
