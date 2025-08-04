#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查DDoS检测结果
"""

import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dl_ids.settings')
django.setup()

from main.models import TrafficLog
from datetime import datetime, timedelta
from collections import Counter

def main():
    print("=" * 60)
    print("DDoS Detection Results Check")
    print("=" * 60)

    # Get all records
    total_records = TrafficLog.objects.count()
    print(f"Total records in database: {total_records}")

    if total_records == 0:
        print("❌ No traffic records in database")
        return

    # Get recent records
    recent_logs = TrafficLog.objects.all().order_by('-create_time')[:30]

    print(f"\nRecent 30 records:")
    print("-" * 60)
    
    attack_types = Counter()
    ddos_count = 0
    
    for i, log in enumerate(recent_logs):
        attack_types[log.attack_type] += 1
        if log.attack_type == 'DosFam':
            ddos_count += 1
        
        time_str = log.create_time.strftime("%H:%M:%S")
        print(f"{i+1:2d}. {time_str} - {log.src_ip} -> {log.dst_ip} - {log.attack_type} - {log.threat}")
    
    print("\n" + "=" * 60)
    print("Detection Results Statistics:")
    print("=" * 60)
    
    for attack_type, count in attack_types.most_common():
        percentage = (count / len(recent_logs)) * 100
        print(f"{attack_type:15}: {count:4d} times ({percentage:5.1f}%)")
    
    if ddos_count > 0:
        print(f"\n✅ Successfully detected {ddos_count} DDoS attacks!")
        print("🎯 Deep learning DDoS detection system is working properly!")
    else:
        print("\n❌ No DDoS attacks detected")

if __name__ == "__main__":
    main()
