#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import logging
from datetime import datetime
import pandas as pd
import os

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path='scada_data.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建数据记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recording_id TEXT,
                    timestamp DATETIME,
                    in1_current REAL,
                    in1_voltage REAL,
                    in2_current REAL,
                    in2_voltage REAL,
                    in3_current REAL,
                    in3_voltage REAL,
                    in4_current REAL,
                    in4_voltage REAL,
                    in5_current REAL,
                    in5_voltage REAL,
                    in6_current REAL,
                    in6_voltage REAL,
                    in7_current REAL,
                    in7_voltage REAL,
                    in8_current REAL,
                    in8_voltage REAL,
                    in9_current REAL,
                    in9_voltage REAL,
                    in10_current REAL,
                    in10_voltage REAL,
                    ac_current REAL,
                    vbat_voltage REAL,
                    temperature REAL,
                    humidity REAL,
                    door_status INTEGER,
                    water_status INTEGER,
                    ac_status INTEGER,
                    battery1_voltage REAL,
                    battery2_voltage REAL,
                    battery3_voltage REAL,
                    battery4_voltage REAL,
                    battery5_voltage REAL,
                    battery6_voltage REAL,
                    battery7_voltage REAL,
                    battery8_voltage REAL,
                    total_voltage REAL,
                    current REAL,
                    temperature1 REAL,
                    temperature2 REAL,
                    balance_status INTEGER,
                    charge_discharge_status INTEGER,
                    battery_percentage INTEGER
                )
            ''')
            
            # 创建记录会话表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recording_sessions (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    start_time DATETIME,
                    end_time DATETIME
                )
            ''')
            
            # 创建通信日志表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS communication_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    message TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("数据库初始化完成")
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            
    def start_recording(self, name):
        """开始数据记录"""
        try:
            recording_id = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO recording_sessions (id, name, start_time) VALUES (?, ?, ?)',
                (recording_id, name, datetime.now())
            )
            conn.commit()
            conn.close()
            
            logger.info(f"开始数据记录: {name} (ID: {recording_id})")
            return recording_id
        except Exception as e:
            logger.error(f"开始记录失败: {str(e)}")
            return None
            
    def stop_recording(self, recording_id):
        """停止数据记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE recording_sessions SET end_time = ? WHERE id = ?',
                (datetime.now(), recording_id)
            )
            conn.commit()
            conn.close()
            
            logger.info(f"停止数据记录: ID {recording_id}")
            return True
        except Exception as e:
            logger.error(f"停止记录失败: {str(e)}")
            return False
            
    def save_data(self, recording_id, board_data, bms_data):
        """保存数据到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO data_records (
                    recording_id, timestamp,
                    in1_current, in1_voltage, in2_current, in2_voltage,
                    in3_current, in3_voltage, in4_current, in4_voltage,
                    in5_current, in5_voltage, in6_current, in6_voltage,
                    in7_current, in7_voltage, in8_current, in8_voltage,
                    in9_current, in9_voltage, in10_current, in10_voltage,
                    ac_current, vbat_voltage, temperature, humidity,
                    door_status, water_status, ac_status,
                    battery1_voltage, battery2_voltage, battery3_voltage, battery4_voltage,
                    battery5_voltage, battery6_voltage, battery7_voltage, battery8_voltage,
                    total_voltage, current, temperature1, temperature2,
                    balance_status, charge_discharge_status, battery_percentage
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                recording_id,
                datetime.now(),
                board_data.get('IN1_current', 0), board_data.get('IN1_voltage', 0),
                board_data.get('IN2_current', 0), board_data.get('IN2_voltage', 0),
                board_data.get('IN3_current', 0), board_data.get('IN3_voltage', 0),
                board_data.get('IN4_current', 0), board_data.get('IN4_voltage', 0),
                board_data.get('IN5_current', 0), board_data.get('IN5_voltage', 0),
                board_data.get('IN6_current', 0), board_data.get('IN6_voltage', 0),
                board_data.get('IN7_current', 0), board_data.get('IN7_voltage', 0),
                board_data.get('IN8_current', 0), board_data.get('IN8_voltage', 0),
                board_data.get('IN9_current', 0), board_data.get('IN9_voltage', 0),
                board_data.get('IN10_current', 0), board_data.get('IN10_voltage', 0),
                board_data.get('AC_current', 0), board_data.get('VBAT_voltage', 0),
                board_data.get('temperature_value', 0), board_data.get('humidity', 0),
                board_data.get('door_status', 0), board_data.get('water_status', 0), board_data.get('ac_status', 0),
                bms_data.get('battery1_voltage', 0), bms_data.get('battery2_voltage', 0),
                bms_data.get('battery3_voltage', 0), bms_data.get('battery4_voltage', 0),
                bms_data.get('battery5_voltage', 0), bms_data.get('battery6_voltage', 0),
                bms_data.get('battery7_voltage', 0), bms_data.get('battery8_voltage', 0),
                bms_data.get('total_voltage', 0), bms_data.get('current', 0),
                bms_data.get('temperature1', 0), bms_data.get('temperature2', 0),
                bms_data.get('balance_status', 0), bms_data.get('charge_discharge_status', 0),
                bms_data.get('battery_percentage', 0)
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"保存数据记录: ID {recording_id}")
            return True
        except Exception as e:
            logger.error(f"保存数据失败: {str(e)}")
            return False
            
    def get_recordings(self):
        """获取所有记录会话"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, start_time, end_time FROM recording_sessions ORDER BY start_time DESC')
            recordings = cursor.fetchall()
            conn.close()
            
            return recordings
        except Exception as e:
            logger.error(f"获取记录会话失败: {str(e)}")
            return []
            
    def delete_recording(self, recording_id):
        """删除指定记录会话"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 删除数据记录
            cursor.execute('DELETE FROM data_records WHERE recording_id = ?', (recording_id,))
            
            # 删除记录会话
            cursor.execute('DELETE FROM recording_sessions WHERE id = ?', (recording_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"删除记录会话: ID {recording_id}")
            return True
        except Exception as e:
            logger.error(f"删除记录会话失败: {str(e)}")
            return False
            
    def export_recording_to_excel(self, recording_id, file_path):
        """将指定记录导出为Excel文件"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # 查询记录会话信息
            session_query = '''
                SELECT name, start_time, end_time 
                FROM recording_sessions 
                WHERE id = ?
            '''
            session_info = pd.read_sql_query(session_query, conn, params=(recording_id,))
            
            if session_info.empty:
                logger.error(f"未找到记录会话: ID {recording_id}")
                return False
            
            # 查询数据记录
            data_query = '''
                SELECT timestamp,
                    in1_current, in1_voltage, in2_current, in2_voltage,
                    in3_current, in3_voltage, in4_current, in4_voltage,
                    in5_current, in5_voltage, in6_current, in6_voltage,
                    in7_current, in7_voltage, in8_current, in8_voltage,
                    in9_current, in9_voltage, in10_current, in10_voltage,
                    ac_current, vbat_voltage, temperature, humidity,
                    door_status, water_status, ac_status,
                    battery1_voltage, battery2_voltage, battery3_voltage, battery4_voltage,
                    battery5_voltage, battery6_voltage, battery7_voltage, battery8_voltage,
                    total_voltage, current, temperature1, temperature2,
                    balance_status, charge_discharge_status, battery_percentage
                FROM data_records 
                WHERE recording_id = ? 
                ORDER BY timestamp
            '''
            data_df = pd.read_sql_query(data_query, conn, params=(recording_id,))
            
            conn.close()
            
            if data_df.empty:
                logger.warning(f"记录会话中没有数据: ID {recording_id}")
                # 创建一个空的DataFrame，但包含列名
                data_df = pd.DataFrame(columns=[
                    'timestamp',
                    'in1_current', 'in1_voltage', 'in2_current', 'in2_voltage',
                    'in3_current', 'in3_voltage', 'in4_current', 'in4_voltage',
                    'in5_current', 'in5_voltage', 'in6_current', 'in6_voltage',
                    'in7_current', 'in7_voltage', 'in8_current', 'in8_voltage',
                    'in9_current', 'in9_voltage', 'in10_current', 'in10_voltage',
                    'ac_current', 'vbat_voltage', 'temperature', 'humidity',
                    'door_status', 'water_status', 'ac_status',
                    'battery1_voltage', 'battery2_voltage', 'battery3_voltage', 'battery4_voltage',
                    'battery5_voltage', 'battery6_voltage', 'battery7_voltage', 'battery8_voltage',
                    'total_voltage', 'current', 'temperature1', 'temperature2',
                    'balance_status', 'charge_discharge_status', 'battery_percentage'
                ])
            
            # 创建Excel写入器
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # 写入会话信息
                session_info.to_excel(writer, sheet_name='会话信息', index=False)
                
                # 写入数据记录
                data_df.to_excel(writer, sheet_name='数据记录', index=False)
                
                # 如果有数据，创建图表数据摘要
                if not data_df.empty:
                    # 创建摘要统计
                    summary_data = {
                        '参数': [
                            '记录总数', '开始时间', '结束时间', '持续时间(分钟)',
                            'IN1电流(平均)', 'IN1电压(平均)', 
                            '电池总电压(平均)', '电流(平均)',
                            '温度1(平均)', '温度2(平均)',
                            '电池电量(平均)'
                        ],
                        '值': [
                            len(data_df),
                            data_df['timestamp'].min() if not data_df.empty else 'N/A',
                            data_df['timestamp'].max() if not data_df.empty else 'N/A',
                            round((pd.to_datetime(data_df['timestamp'].max()) - pd.to_datetime(data_df['timestamp'].min())).total_seconds() / 60, 2) if not data_df.empty and len(data_df) > 1 else 'N/A',
                            round(data_df['in1_current'].mean(), 2) if not data_df.empty else 'N/A',
                            round(data_df['in1_voltage'].mean(), 2) if not data_df.empty else 'N/A',
                            round(data_df['total_voltage'].mean(), 2) if not data_df.empty else 'N/A',
                            round(data_df['current'].mean(), 2) if not data_df.empty else 'N/A',
                            round(data_df['temperature1'].mean(), 2) if not data_df.empty else 'N/A',
                            round(data_df['temperature2'].mean(), 2) if not data_df.empty else 'N/A',
                            round(data_df['battery_percentage'].mean(), 2) if not data_df.empty else 'N/A'
                        ]
                    }
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='数据摘要', index=False)
            
            logger.info(f"记录导出完成: ID {recording_id} -> {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出记录失败: {str(e)}")
            return False
            
    def add_log_entry(self, message):
        """添加通信日志条目"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO communication_logs (timestamp, message) VALUES (?, ?)',
                (datetime.now(), message)
            )
            conn.commit()
            conn.close()
            
            logger.info(f"添加日志条目: {message}")
            return True
        except Exception as e:
            logger.error(f"添加日志条目失败: {str(e)}")
            return False
            
    def get_logs(self, limit=100):
        """获取最近的通信日志"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT timestamp, message FROM communication_logs ORDER BY timestamp DESC LIMIT ?', (limit,))
            logs = cursor.fetchall()
            conn.close()
            
            return logs
        except Exception as e:
            logger.error(f"获取日志失败: {str(e)}")
            return []