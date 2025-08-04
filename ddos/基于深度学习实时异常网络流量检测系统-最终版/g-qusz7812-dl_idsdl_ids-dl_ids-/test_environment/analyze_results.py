#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检测结果分析脚本
分析深度学习网络流量异常检测系统的测试结果
"""

import os
import sys
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from collections import Counter
import json

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class ResultAnalyzer:
    def __init__(self, db_path="../db.sqlite3"):
        self.db_path = db_path
        self.conn = None
        
    def connect_db(self):
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            print(f"✓ 成功连接数据库: {self.db_path}")
            return True
        except Exception as e:
            print(f"✗ 数据库连接失败: {e}")
            return False
    
    def get_traffic_logs(self, hours=24):
        """获取流量日志"""
        if not self.conn:
            return None
            
        try:
            # 获取最近N小时的数据
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            query = """
            SELECT src_ip, dst_ip, src_port, dst_port, protocol, 
                   attack_type, threat, create_time, features
            FROM tb_packetbaseinfo 
            WHERE create_time >= ?
            ORDER BY create_time DESC
            """
            
            df = pd.read_sql_query(query, self.conn, params=[cutoff_time])
            print(f"✓ 获取到 {len(df)} 条流量记录")
            return df
            
        except Exception as e:
            print(f"✗ 获取流量日志失败: {e}")
            return None
    
    def analyze_attack_types(self, df):
        """分析攻击类型分布"""
        if df is None or df.empty:
            print("没有数据可分析")
            return
            
        print("\n" + "="*50)
        print("攻击类型分析")
        print("="*50)
        
        # 统计攻击类型
        attack_counts = df['attack_type'].value_counts()
        print("\n攻击类型分布:")
        for attack_type, count in attack_counts.items():
            if pd.notna(attack_type):
                print(f"  {attack_type}: {count} 次")
        
        # 绘制攻击类型分布图
        plt.figure(figsize=(12, 6))
        
        plt.subplot(1, 2, 1)
        attack_counts.plot(kind='bar')
        plt.title('攻击类型分布')
        plt.xlabel('攻击类型')
        plt.ylabel('检测次数')
        plt.xticks(rotation=45)
        
        # 威胁级别分布
        plt.subplot(1, 2, 2)
        threat_counts = df['threat'].value_counts()
        threat_counts.plot(kind='pie', autopct='%1.1f%%')
        plt.title('威胁级别分布')
        
        plt.tight_layout()
        plt.savefig('attack_analysis.png', dpi=300, bbox_inches='tight')
        print("✓ 攻击分析图表已保存为 attack_analysis.png")
        
        return attack_counts
    
    def analyze_time_distribution(self, df):
        """分析时间分布"""
        if df is None or df.empty:
            return
            
        print("\n" + "="*50)
        print("时间分布分析")
        print("="*50)
        
        # 转换时间格式
        df['create_time'] = pd.to_datetime(df['create_time'])
        df['hour'] = df['create_time'].dt.hour
        df['minute'] = df['create_time'].dt.minute
        
        # 按小时统计
        hourly_counts = df.groupby('hour').size()
        print("\n每小时检测数量:")
        for hour, count in hourly_counts.items():
            print(f"  {hour:02d}:00 - {count} 次")
        
        # 绘制时间分布图
        plt.figure(figsize=(15, 5))
        
        plt.subplot(1, 3, 1)
        hourly_counts.plot(kind='bar')
        plt.title('每小时检测数量')
        plt.xlabel('小时')
        plt.ylabel('检测次数')
        
        plt.subplot(1, 3, 2)
        # 按攻击类型和时间分组
        attack_time = df.groupby(['hour', 'attack_type']).size().unstack(fill_value=0)
        attack_time.plot(kind='bar', stacked=True)
        plt.title('每小时攻击类型分布')
        plt.xlabel('小时')
        plt.ylabel('检测次数')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.subplot(1, 3, 3)
        # 最近1小时的分钟级分布
        recent_hour = df[df['create_time'] >= datetime.now() - timedelta(hours=1)]
        if not recent_hour.empty:
            minute_counts = recent_hour.groupby('minute').size()
            minute_counts.plot(kind='line', marker='o')
            plt.title('最近1小时分钟级检测')
            plt.xlabel('分钟')
            plt.ylabel('检测次数')
        
        plt.tight_layout()
        plt.savefig('time_analysis.png', dpi=300, bbox_inches='tight')
        print("✓ 时间分析图表已保存为 time_analysis.png")
    
    def analyze_ip_statistics(self, df):
        """分析IP统计"""
        if df is None or df.empty:
            return
            
        print("\n" + "="*50)
        print("IP地址分析")
        print("="*50)
        
        # 源IP统计
        src_ip_counts = df['src_ip'].value_counts().head(10)
        print("\n最活跃的源IP地址:")
        for ip, count in src_ip_counts.items():
            print(f"  {ip}: {count} 次")
        
        # 目标IP统计
        dst_ip_counts = df['dst_ip'].value_counts().head(10)
        print("\n最常被攻击的目标IP:")
        for ip, count in dst_ip_counts.items():
            print(f"  {ip}: {count} 次")
        
        # 端口统计
        port_counts = df['dst_port'].value_counts().head(10)
        print("\n最常被攻击的端口:")
        for port, count in port_counts.items():
            print(f"  {port}: {count} 次")
        
        # 绘制IP和端口分析图
        plt.figure(figsize=(15, 10))
        
        plt.subplot(2, 2, 1)
        src_ip_counts.plot(kind='barh')
        plt.title('最活跃源IP地址')
        plt.xlabel('检测次数')
        
        plt.subplot(2, 2, 2)
        dst_ip_counts.plot(kind='barh')
        plt.title('最常被攻击目标IP')
        plt.xlabel('检测次数')
        
        plt.subplot(2, 2, 3)
        port_counts.plot(kind='bar')
        plt.title('最常被攻击端口')
        plt.xlabel('端口')
        plt.ylabel('检测次数')
        plt.xticks(rotation=45)
        
        plt.subplot(2, 2, 4)
        protocol_counts = df['protocol'].value_counts()
        protocol_counts.plot(kind='pie', autopct='%1.1f%%')
        plt.title('协议分布')
        
        plt.tight_layout()
        plt.savefig('ip_analysis.png', dpi=300, bbox_inches='tight')
        print("✓ IP分析图表已保存为 ip_analysis.png")
    
    def generate_summary_report(self, df):
        """生成汇总报告"""
        if df is None or df.empty:
            return
            
        print("\n" + "="*50)
        print("检测系统性能汇总")
        print("="*50)
        
        total_records = len(df)
        attack_records = len(df[df['attack_type'].notna()])
        normal_records = total_records - attack_records
        
        print(f"\n总检测记录数: {total_records}")
        print(f"异常流量记录: {attack_records}")
        print(f"正常流量记录: {normal_records}")
        
        if total_records > 0:
            attack_rate = (attack_records / total_records) * 100
            print(f"异常检测率: {attack_rate:.2f}%")
        
        # 时间范围
        if not df.empty:
            df['create_time'] = pd.to_datetime(df['create_time'])
            start_time = df['create_time'].min()
            end_time = df['create_time'].max()
            duration = end_time - start_time
            
            print(f"\n分析时间范围:")
            print(f"开始时间: {start_time}")
            print(f"结束时间: {end_time}")
            print(f"持续时间: {duration}")
            
            if duration.total_seconds() > 0:
                avg_rate = total_records / duration.total_seconds()
                print(f"平均检测速率: {avg_rate:.2f} 记录/秒")
        
        # 生成JSON报告
        report = {
            'summary': {
                'total_records': total_records,
                'attack_records': attack_records,
                'normal_records': normal_records,
                'attack_rate': attack_rate if total_records > 0 else 0,
                'analysis_time': datetime.now().isoformat()
            },
            'attack_types': df['attack_type'].value_counts().to_dict(),
            'threat_levels': df['threat'].value_counts().to_dict(),
            'top_source_ips': df['src_ip'].value_counts().head(5).to_dict(),
            'top_target_ports': df['dst_port'].value_counts().head(5).to_dict()
        }
        
        with open('detection_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print("✓ 详细报告已保存为 detection_report.json")
    
    def run_analysis(self, hours=24):
        """运行完整分析"""
        print("深度学习网络流量异常检测系统 - 结果分析")
        print("="*60)
        
        if not self.connect_db():
            return False
        
        # 获取数据
        df = self.get_traffic_logs(hours)
        if df is None:
            return False
        
        if df.empty:
            print("没有找到检测记录，请确保:")
            print("1. 系统已运行并检测到流量")
            print("2. 数据库路径正确")
            print("3. 时间范围内有数据")
            return False
        
        # 执行各项分析
        self.analyze_attack_types(df)
        self.analyze_time_distribution(df)
        self.analyze_ip_statistics(df)
        self.generate_summary_report(df)
        
        print("\n" + "="*60)
        print("分析完成！生成的文件:")
        print("- attack_analysis.png: 攻击类型分析图")
        print("- time_analysis.png: 时间分布分析图")
        print("- ip_analysis.png: IP和端口分析图")
        print("- detection_report.json: 详细JSON报告")
        print("="*60)
        
        return True
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='检测结果分析工具')
    parser.add_argument('--db', default='../db.sqlite3', help='数据库文件路径')
    parser.add_argument('--hours', type=int, default=24, help='分析最近N小时的数据')
    parser.add_argument('--show', action='store_true', help='显示图表')
    
    args = parser.parse_args()
    
    # 检查数据库文件
    if not os.path.exists(args.db):
        print(f"错误: 数据库文件不存在: {args.db}")
        print("请确保Django项目已运行并生成了数据库文件")
        sys.exit(1)
    
    # 运行分析
    analyzer = ResultAnalyzer(args.db)
    
    try:
        success = analyzer.run_analysis(args.hours)
        
        if success and args.show:
            plt.show()
            
    except KeyboardInterrupt:
        print("\n用户中断分析")
    except Exception as e:
        print(f"分析过程中出错: {e}")
    finally:
        analyzer.close()

if __name__ == "__main__":
    main()
