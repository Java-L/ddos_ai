#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中的DDoS检测记录
"""

import os
import sys
import django

# 设置Django环境
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
os.chdir(parent_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dl_ids.settings')
django.setup()

from main.models import TrafficLog
from datetime import datetime, timedelta
from collections import Counter

def check_ddos_detection():
    """检查DDoS检测结果"""
    print("=" * 60)
    print("DDoS检测结果检查")
    print("=" * 60)
    
    # 获取所有记录
    total_records = TrafficLog.objects.count()
    print(f"数据库中总记录数: {total_records}")
    
    if total_records == 0:
        print("❌ 数据库中没有流量记录")
        print("可能原因:")
        print("1. DDoS中间件未正确加载")
        print("2. 攻击测试未正确执行")
        print("3. 数据库连接问题")
        return
    
    # 获取最近的记录
    recent_logs = TrafficLog.objects.all().order_by('-created_at')[:50]
    
    print(f"\n最近50条记录:")
    print("-" * 60)
    
    attack_types = Counter()
    threat_levels = Counter()
    ddos_records = []
    
    for i, log in enumerate(recent_logs):
        attack_types[log.attack_type] += 1
        threat_levels[log.threat_level] += 1
        
        if log.attack_type == 'DosFam':
            ddos_records.append(log)
        
        time_str = log.created_at.strftime("%H:%M:%S")
        print(f"{i+1:2d}. {time_str} - {log.src_ip} -> {log.dst_ip} - {log.attack_type} - {log.threat_level}")
    
    print("\n" + "=" * 60)
    print("统计结果:")
    print("=" * 60)
    
    print("攻击类型分布:")
    for attack_type, count in attack_types.most_common():
        percentage = (count / len(recent_logs)) * 100
        print(f"  {attack_type:15}: {count:4d} 次 ({percentage:5.1f}%)")
    
    print("\n威胁级别分布:")
    for threat_level, count in threat_levels.most_common():
        percentage = (count / len(recent_logs)) * 100
        print(f"  {threat_level:15}: {count:4d} 次 ({percentage:5.1f}%)")
    
    # DDoS检测分析
    ddos_count = len(ddos_records)
    print(f"\n" + "=" * 60)
    print("DDoS检测分析:")
    print("=" * 60)
    
    if ddos_count > 0:
        print(f"✅ 成功检测到 {ddos_count} 次 DDoS 攻击!")
        
        # 分析DDoS记录的威胁级别
        ddos_threat_levels = Counter()
        for record in ddos_records:
            ddos_threat_levels[record.threat_level] += 1
        
        print("DDoS攻击威胁级别:")
        for level, count in ddos_threat_levels.most_common():
            print(f"  {level}: {count} 次")
        
        # 显示最近的DDoS攻击
        print(f"\n最近的DDoS攻击记录 (前10条):")
        for i, record in enumerate(ddos_records[:10]):
            time_str = record.created_at.strftime("%H:%M:%S")
            print(f"  {i+1:2d}. {time_str} - {record.src_ip} - {record.threat_level}")
        
        print(f"\n🎯 测试结论:")
        print(f"   深度学习DDoS检测系统工作正常!")
        print(f"   成功识别了 {ddos_count} 次 DDoS 攻击")
        print(f"   检测率: {(ddos_count / len(recent_logs)) * 100:.1f}%")
        
    else:
        print("❌ 未检测到 DDoS 攻击")
        print("可能原因:")
        print("1. 中间件配置问题")
        print("2. 攻击特征识别失败")
        print("3. 数据记录延迟")
        
        # 检查是否有其他类型的攻击被检测到
        if attack_types:
            print("\n但检测到了其他类型的流量:")
            for attack_type, count in attack_types.most_common():
                if attack_type != 'DosFam':
                    print(f"  {attack_type}: {count} 次")

if __name__ == "__main__":
    try:
        check_ddos_detection()
    except Exception as e:
        print(f"检查过程中出错: {e}")
        import traceback
        traceback.print_exc()
