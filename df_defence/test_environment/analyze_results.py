#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detection Results Analysis Script
Analyze test results of deep learning network traffic anomaly detection system
检测结果分析脚本 - 分析深度学习网络流量异常检测系统的测试结果
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

# Set Chinese font for matplotlib / 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class ResultAnalyzer:
    def __init__(self, db_path="../db.sqlite3"):
        self.db_path = db_path
        self.conn = None

    def connect_db(self):
        """Connect to database / 连接数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            print(f"✓ Successfully connected to database: {self.db_path}")
            return True
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False
    
    def get_traffic_logs(self, hours=24):
        """Get traffic logs / 获取流量日志"""
        if not self.conn:
            return None

        try:
            # Get data from the last N hours / 获取最近N小时的数据
            cutoff_time = datetime.now() - timedelta(hours=hours)

            query = """
            SELECT src_ip, dst_ip, src_port, dst_port, protocol,
                   attack_type, threat, create_time, features
            FROM tb_packetbaseinfo
            WHERE create_time >= ?
            ORDER BY create_time DESC
            """

            df = pd.read_sql_query(query, self.conn, params=[cutoff_time])
            print(f"✓ Retrieved {len(df)} traffic records")
            return df

        except Exception as e:
            print(f"✗ Failed to retrieve traffic logs: {e}")
            return None
    
    def analyze_attack_types(self, df):
        """Analyze attack type distribution / 分析攻击类型分布"""
        if df is None or df.empty:
            print("No data to analyze")
            return

        print("\n" + "="*50)
        print("Attack Type Analysis")
        print("="*50)

        # Count attack types / 统计攻击类型
        attack_counts = df['attack_type'].value_counts()
        print("\nAttack Type Distribution:")
        for attack_type, count in attack_counts.items():
            if pd.notna(attack_type):
                print(f"  {attack_type}: {count} times")

        # Plot attack type distribution / 绘制攻击类型分布图
        plt.figure(figsize=(12, 6))

        plt.subplot(1, 2, 1)
        attack_counts.plot(kind='bar')
        plt.title('Attack Type Distribution')
        plt.xlabel('Attack Type')
        plt.ylabel('Detection Count')
        plt.xticks(rotation=45)

        # Threat level distribution / 威胁级别分布
        plt.subplot(1, 2, 2)
        threat_counts = df['threat'].value_counts()
        threat_counts.plot(kind='pie', autopct='%1.1f%%')
        plt.title('Threat Level Distribution')

        plt.tight_layout()
        plt.savefig('attack_analysis.png', dpi=300, bbox_inches='tight')
        print("✓ Attack analysis chart saved as attack_analysis.png")

        return attack_counts
    
    def analyze_time_distribution(self, df):
        """Analyze time distribution / 分析时间分布"""
        if df is None or df.empty:
            return

        print("\n" + "="*50)
        print("Time Distribution Analysis")
        print("="*50)

        # Convert time format / 转换时间格式
        df['create_time'] = pd.to_datetime(df['create_time'])
        df['hour'] = df['create_time'].dt.hour
        df['minute'] = df['create_time'].dt.minute

        # Count by hour / 按小时统计
        hourly_counts = df.groupby('hour').size()
        print("\nHourly Detection Count:")
        for hour, count in hourly_counts.items():
            print(f"  {hour:02d}:00 - {count} times")

        # Plot time distribution / 绘制时间分布图
        plt.figure(figsize=(15, 5))

        plt.subplot(1, 3, 1)
        hourly_counts.plot(kind='bar')
        plt.title('Hourly Detection Count')
        plt.xlabel('Hour')
        plt.ylabel('Detection Count')

        plt.subplot(1, 3, 2)
        # Group by attack type and time / 按攻击类型和时间分组
        attack_time = df.groupby(['hour', 'attack_type']).size().unstack(fill_value=0)
        attack_time.plot(kind='bar', stacked=True)
        plt.title('Hourly Attack Type Distribution')
        plt.xlabel('Hour')
        plt.ylabel('Detection Count')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

        plt.subplot(1, 3, 3)
        # Minute-level distribution for the last hour / 最近1小时的分钟级分布
        recent_hour = df[df['create_time'] >= datetime.now() - timedelta(hours=1)]
        if not recent_hour.empty:
            minute_counts = recent_hour.groupby('minute').size()
            minute_counts.plot(kind='line', marker='o')
            plt.title('Last Hour Minute-level Detection')
            plt.xlabel('Minute')
            plt.ylabel('Detection Count')

        plt.tight_layout()
        plt.savefig('time_analysis.png', dpi=300, bbox_inches='tight')
        print("✓ Time analysis chart saved as time_analysis.png")

    def analyze_ip_statistics(self, df):
        """Analyze IP statistics / 分析IP统计"""
        if df is None or df.empty:
            return

        print("\n" + "="*50)
        print("IP Address Analysis")
        print("="*50)

        # Source IP statistics / 源IP统计
        src_ip_counts = df['src_ip'].value_counts().head(10)
        print("\nMost Active Source IP Addresses:")
        for ip, count in src_ip_counts.items():
            print(f"  {ip}: {count} times")

        # Target IP statistics / 目标IP统计
        dst_ip_counts = df['dst_ip'].value_counts().head(10)
        print("\nMost Attacked Target IPs:")
        for ip, count in dst_ip_counts.items():
            print(f"  {ip}: {count} times")

        # Port statistics / 端口统计
        port_counts = df['dst_port'].value_counts().head(10)
        print("\nMost Attacked Ports:")
        for port, count in port_counts.items():
            print(f"  {port}: {count} times")

        # Plot IP and port analysis / 绘制IP和端口分析图
        plt.figure(figsize=(15, 10))

        plt.subplot(2, 2, 1)
        src_ip_counts.plot(kind='barh')
        plt.title('Most Active Source IPs')
        plt.xlabel('Detection Count')

        plt.subplot(2, 2, 2)
        dst_ip_counts.plot(kind='barh')
        plt.title('Most Attacked Target IPs')
        plt.xlabel('Detection Count')

        plt.subplot(2, 2, 3)
        port_counts.plot(kind='bar')
        plt.title('Most Attacked Ports')
        plt.xlabel('Port')
        plt.ylabel('Detection Count')
        plt.xticks(rotation=45)

        plt.subplot(2, 2, 4)
        protocol_counts = df['protocol'].value_counts()
        protocol_counts.plot(kind='pie', autopct='%1.1f%%')
        plt.title('Protocol Distribution')

        plt.tight_layout()
        plt.savefig('ip_analysis.png', dpi=300, bbox_inches='tight')
        print("✓ IP analysis chart saved as ip_analysis.png")

    def generate_summary_report(self, df):
        """Generate summary report / 生成汇总报告"""
        if df is None or df.empty:
            return

        print("\n" + "="*50)
        print("Detection System Performance Summary")
        print("="*50)

        total_records = len(df)
        attack_records = len(df[df['attack_type'].notna()])
        normal_records = total_records - attack_records

        print(f"\nTotal Detection Records: {total_records}")
        print(f"Anomalous Traffic Records: {attack_records}")
        print(f"Normal Traffic Records: {normal_records}")

        if total_records > 0:
            attack_rate = (attack_records / total_records) * 100
            print(f"Anomaly Detection Rate: {attack_rate:.2f}%")

        # Time range / 时间范围
        if not df.empty:
            df['create_time'] = pd.to_datetime(df['create_time'])
            start_time = df['create_time'].min()
            end_time = df['create_time'].max()
            duration = end_time - start_time

            print(f"\nAnalysis Time Range:")
            print(f"Start Time: {start_time}")
            print(f"End Time: {end_time}")
            print(f"Duration: {duration}")

            if duration.total_seconds() > 0:
                avg_rate = total_records / duration.total_seconds()
                print(f"Average Detection Rate: {avg_rate:.2f} records/sec")

        # Generate JSON report / 生成JSON报告
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

        print("✓ Detailed report saved as detection_report.json")

    def run_analysis(self, hours=24):
        """Run complete analysis / 运行完整分析"""
        print("Deep Learning Network Traffic Anomaly Detection System - Result Analysis")
        print("="*60)

        if not self.connect_db():
            return False

        # Get data / 获取数据
        df = self.get_traffic_logs(hours)
        if df is None:
            return False

        if df.empty:
            print("No detection records found, please ensure:")
            print("1. System is running and detecting traffic")
            print("2. Database path is correct")
            print("3. Data exists within the time range")
            return False

        # Execute various analyses / 执行各项分析
        self.analyze_attack_types(df)
        self.analyze_time_distribution(df)
        self.analyze_ip_statistics(df)
        self.generate_summary_report(df)

        print("\n" + "="*60)
        print("Analysis completed! Generated files:")
        print("- attack_analysis.png: Attack type analysis chart")
        print("- time_analysis.png: Time distribution analysis chart")
        print("- ip_analysis.png: IP and port analysis chart")
        print("- detection_report.json: Detailed JSON report")
        print("="*60)

        return True

    def close(self):
        """Close database connection / 关闭数据库连接"""
        if self.conn:
            self.conn.close()

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Detection result analysis tool')
    parser.add_argument('--db', default='../db.sqlite3', help='Database file path')
    parser.add_argument('--hours', type=int, default=24, help='Analyze data from the last N hours')
    parser.add_argument('--show', action='store_true', help='Display charts')

    args = parser.parse_args()

    # Check database file / 检查数据库文件
    if not os.path.exists(args.db):
        print(f"Error: Database file does not exist: {args.db}")
        print("Please ensure Django project is running and database file is generated")
        sys.exit(1)

    # Run analysis / 运行分析
    analyzer = ResultAnalyzer(args.db)

    try:
        success = analyzer.run_analysis(args.hours)

        if success and args.show:
            plt.show()

    except KeyboardInterrupt:
        print("\nUser interrupted analysis")
    except Exception as e:
        print(f"Error during analysis: {e}")
    finally:
        analyzer.close()

if __name__ == "__main__":
    main()
