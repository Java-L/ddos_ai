# tools/security_data_fetcher.py
from datetime import datetime, timedelta, date
from django.db import connection, transaction


class SQLFather:
    """通用安全数据获取类"""

    def __init__(self):
        """初始化数据库连接"""
        self.connection = connection

    # 将流量数据插入到数据库表中
    def insertPacket(self, data):
        """
        将流量数据插入到数据库表 tb_packet 中
        :param data: 包含流量数据的字典
        :return: None
        """
        try:
            with connection.cursor() as cursor:
                # 构造插入 SQL 语句
                query = """
                    INSERT INTO tb_packetbaseinfo (
                        src_ip, dst_ip, src_port, dst_port, protocol, 
                        features,create_time, 
                        attack_type, threat
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """
                # 提取数据并按字段顺序传入
                values = (
                    data.get('src_ip'),
                    data.get('dst_ip'),
                    data.get('src_port'),
                    data.get('dst_port'),
                    data.get('protocol'),
                    data.get('features'),
                    data.get('create_time'),
                    data.get('attack_type'),
                    data.get('threat')
                )
                # 执行插入
                cursor.execute(query, values)
                # 提交事务（如果需要）
                connection.commit()

        except Exception as e:
            # 回滚事务（如果需要）
            connection.rollback()
            raise Exception(f"Traffic-Database insertion failed: {str(e)}")

    def getTrafficLogs(self, start_time=None, end_time=None, status=None, attack_type=None, page_size=None):
        """
        Get traffic log data
        :param start_time: Start time
        :param end_time: End time
        :param status: Threat level
        :param attack_type: Attack type
        :param page_size: Number of records to return
        :return: (total count, record list)
        """
        try:
            with connection.cursor() as cursor:
                # Build base query
                base_query = """
                    SELECT 
                        id, src_ip, dst_ip, src_port, dst_port, 
                        protocol, features, create_time, attack_type, threat
                    FROM tb_packetbaseinfo
                    WHERE 1=1 and attack_type != 'No attack detected'
                """
                params = []

                # Add time conditions
                if start_time:
                    base_query += " AND create_time >= %s"
                    params.append(start_time)
                if end_time:
                    base_query += " AND create_time < %s"
                    params.append(end_time)

                # Add threat level conditions
                if status:
                    base_query += " AND threat = %s"
                    params.append(status)

                # 添加攻击类型条件
                if attack_type:
                    base_query += " AND attack_type = %s"
                    params.append(attack_type)

                # 获取总数
                count_query = f"SELECT COUNT(*) FROM ({base_query}) AS count_table"
                cursor.execute(count_query, params)
                total_count = cursor.fetchone()[0]

                # 添加排序和分页
                base_query += " ORDER BY create_time DESC"
                if page_size:
                    base_query += " LIMIT %s"
                    params.append(page_size)

                # 执行查询
                cursor.execute(base_query, params)
                columns = [col[0] for col in cursor.description]
                records = [dict(zip(columns, row)) for row in cursor.fetchall()]

                return total_count, records

        except Exception as e:
            print(f"查询流量日志失败: {str(e)}")
            return 0, []

    def getAlertStats(self, start_time=None, end_time=None):
        """
        获取告警统计数据
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return: 统计字典
        """
        try:
            with connection.cursor() as cursor:
                # 构建统计查询
                stats_query = """
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN threat = '高危' THEN 1 ELSE 0 END) as high_count,
                        SUM(CASE WHEN threat = '中危' THEN 1 ELSE 0 END) as medium_count,
                        SUM(CASE WHEN threat = '低危' THEN 1 ELSE 0 END) as low_count
                    FROM tb_packetbaseinfo
                    WHERE 1=1 and attack_type != '未检测到攻击'
                """
                cursor.execute(stats_query)
                result = cursor.fetchone()
                
                return {
                    'total': result[0] or 0,
                    'high': result[1] or 0,
                    'medium': result[2] or 0,
                    'low': result[3] or 0
                }

        except Exception as e:
            print(f"获取告警统计失败: {str(e)}")
            return {'total': 0, 'high': 0, 'medium': 0, 'low': 0}

    def getAlertTrend(self, start_time=None):
        """
        获取告警趋势数据（MySQL 8）
        :param start_time: 开始时间 (字符串格式: 'YYYY-MM-DD HH:MM:SS' 或 datetime/date 对象)
        :return: 趋势数据列表，格式为 [{'time_slot': 'HH:00', 'count': int}, ...]
        """
        try:
            # 处理 start_time，默认为今天
            if start_time is None:
                query_date = datetime.now().date()
            elif isinstance(start_time, (datetime, date)):
                query_date = start_time.date() if isinstance(start_time, datetime) else start_time
            elif isinstance(start_time, str):
                query_date = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').date()
            else:
                raise ValueError("Invalid start_time format")

            # 定义 24 小时时间点
            time_points = [f"{h:02d}:00" for h in range(24)]

            with connection.cursor() as cursor:
                # SQL 查询，使用 DATE_FORMAT 确保 time_slot 为 HH:00
                trend_query = """
                    WITH hours AS (
                        SELECT n AS hour
                        FROM (SELECT a.N + b.N * 10 + 1 AS n
                              FROM (SELECT 0 AS N UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) a,
                                   (SELECT 0 AS N UNION ALL SELECT 1 UNION ALL SELECT 2) b
                              ORDER BY n) numbers
                        WHERE n <= 23
                    )
                    SELECT 
                        DATE_FORMAT(MAKETIME(h.hour, 0, 0), '%%H:%%i') AS time_slot,
                        COALESCE(COUNT(t.create_time), 0) AS count
                    FROM hours h
                    LEFT JOIN tb_packetbaseinfo t
                        ON HOUR(t.create_time) = h.hour
                        AND DATE(t.create_time) = %s
                        AND t.attack_type != '未检测到攻击'
                    GROUP BY h.hour
                    ORDER BY h.hour;
                """
                # 执行查询
                cursor.execute(trend_query, [query_date])
                results = cursor.fetchall()

                # 转换为字典格式
                trend_data = {row[0]: row[1] for row in results}

                # 返回按 time_points 顺序的趋势数据
                return [{"time_slot": tp, "count": trend_data.get(tp, 0)} for tp in time_points]

        except Exception as e:
            print(f"Error in getAlertTrend: {e}")
            # 返回默认值，24 小时全为 0
            return [{"time_slot": tp, "count": 0} for tp in [f"{h:02d}:00" for h in range(24)]]

    def getAlertTypes(self, start_time=None, end_time=None):
        """
        获取告警类型分布
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return: 类型分布字典
        """
        try:
            with connection.cursor() as cursor:
                type_query = """
                    SELECT 
                        attack_type,
                        COUNT(*) as count
                    FROM tb_packetbaseinfo
                    WHERE 1=1 and attack_type != '未检测到攻击'
                """
                params = []

                # 添加时间条件
                if start_time:
                    type_query += " AND create_time >= %s"
                    params.append(start_time)
                if end_time:
                    type_query += " AND create_time < %s"
                    params.append(end_time)

                type_query += """
                    GROUP BY attack_type
                    ORDER BY count DESC
                """

                cursor.execute(type_query, params)
                results = cursor.fetchall()
                
                return {row[0]: row[1] for row in results}

        except Exception as e:
            print(f"获取告警类型分布失败: {str(e)}")
            return {}
