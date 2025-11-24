import os
import json
import logging
import sqlite3
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

# 设置环境变量以确保UTF-8编码
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
# 确保日志处理器使用UTF-8编码
for handler in logging.getLogger().handlers:
    if isinstance(handler, logging.StreamHandler):
        handler.stream.reconfigure(encoding='utf-8') if hasattr(handler.stream, 'reconfigure') else None

logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')

# 数据库文件路径
DB_FILE = 'modbus_data.db'

# 存储Modbus连接配置
modbus_config = {
    'host': '127.0.0.1',
    'port': 502
}

# 通信日志
communication_log = []

# 连接状态
connection_status = {
    'connected': False,
    'last_check': None
}

# 记录状态
recording_status = {
    'is_recording': False,
    'recording_id': None
}

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_FILE)
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
    
    conn.commit()
    conn.close()

def log_communication(message):
    """记录通信日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    communication_log.append(log_entry)
    if len(communication_log) > 100:  # 只保留最近100条日志
        communication_log.pop(0)
    logger.info(message)

class ModbusReader:
    def __init__(self):
        self.client = None
    
    def connect(self, host, port):
        """连接到Modbus TCP服务器"""
        try:
            if self.client:
                self.client.close()
            
            self.client = ModbusTcpClient(host, port)
            connection = self.client.connect()
            
            if connection:
                log_communication(f"成功连接到Modbus服务器 {host}:{port}")
                connection_status['connected'] = True
                connection_status['last_check'] = datetime.now().isoformat()
                return True
            else:
                log_communication(f"无法连接到Modbus服务器 {host}:{port}")
                connection_status['connected'] = False
                connection_status['last_check'] = datetime.now().isoformat()
                return False
        except Exception as e:
            log_communication(f"连接Modbus服务器时出错: {str(e)}")
            connection_status['connected'] = False
            connection_status['last_check'] = datetime.now().isoformat()
            return False
    
    def is_connected(self):
        """检查连接状态"""
        if not self.client:
            return False
        try:
            # 尝试读取一个寄存器来检查连接
            result = self.client.read_holding_registers(0x0000, 1, slave=1)
            is_conn = not result.isError()
            connection_status['connected'] = is_conn
            connection_status['last_check'] = datetime.now().isoformat()
            return is_conn
        except:
            connection_status['connected'] = False
            connection_status['last_check'] = datetime.now().isoformat()
            return False
    
    def read_board_data(self):
        """读取二号板数据 (地址 0x0000 - 0x001B)"""
        try:
            if not self.client:
                return None
            
            # 读取电源监测数据 (0x0000 - 0x0015)
            rr = self.client.read_holding_registers(0x0000, 22, slave=1)
            if not rr.isError():
                registers = rr.registers
                
                # 读取环境监测数据和安全状态 (0x0016 - 0x001B)
                data = {
                    # 电源监测数据
                    'IN1_current': registers[0],  # mA
                    'IN1_voltage': registers[1] / 100.0,  # V
                    'IN2_current': registers[2],  # mA
                    'IN2_voltage': registers[3] / 100.0,  # V
                    'IN3_current': registers[4],  # mA
                    'IN3_voltage': registers[5] / 100.0,  # V
                    'IN4_current': registers[6],  # mA
                    'IN4_voltage': registers[7] / 100.0,  # V
                    'IN5_current': registers[8],  # mA
                    'IN5_voltage': registers[9] / 100.0,  # V
                    'IN6_current': registers[10],  # mA
                    'IN6_voltage': registers[11] / 100.0,  # V
                    'IN7_current': registers[12],  # mA
                    'IN7_voltage': registers[13] / 100.0,  # V
                    'IN8_current': registers[14],  # mA
                    'IN8_voltage': registers[15] / 100.0,  # V
                    'IN9_current': registers[16],  # mA
                    'IN9_voltage': registers[17] / 100.0,  # V
                    'IN10_current': registers[18],  # mA
                    'IN10_voltage': registers[19] / 100.0,  # V
                    'AC_current': registers[20],  # A
                    'VBAT_voltage': registers[21] / 100.0,  # V
                    
                    # 环境监测数据
                    'temperature_sign': None,  # 将在下面读取
                    'temperature_value': None,  # 将在下面读取
                    'humidity': None,  # 将在下面读取
                    
                    # 安全状态
                    'door_status': None,  # 将在下面读取
                    'water_status': None,  # 将在下面读取
                    'ac_status': None  # 将在下面读取
                }
                
                log_communication(f"成功读取二号板电源监测数据: {registers[:22]}")
            else:
                log_communication(f"读取二号板电源监测数据失败: {rr}")
                return None
            
            # 读取环境监测数据 (0x0016 - 0x0018)
            rr = self.client.read_holding_registers(0x0016, 3, slave=1)
            if not rr.isError():
                registers = rr.registers
                # 处理温度符号和值
                temp_sign = registers[0]  # 0=正数, 1=负数
                temp_value = registers[1]  # 温度绝对值
                actual_temp = temp_value if temp_sign == 0 else -temp_value
                
                data.update({
                    'temperature_sign': temp_sign,
                    'temperature_value': actual_temp,
                    'humidity': registers[2]  # %RH
                })
                
                log_communication(f"成功读取二号板环境监测数据: {registers}")
            else:
                log_communication(f"读取二号板环境监测数据失败: {rr}")
            
            # 读取安全状态 (0x0019 - 0x001B)
            rr = self.client.read_holding_registers(0x0019, 3, slave=1)
            if not rr.isError():
                registers = rr.registers
                data.update({
                    'door_status': registers[0],  # 1=打开, 0=关闭
                    'water_status': registers[1],  # 1=有水, 0=没水
                    'ac_status': registers[2]  # 0=主电源, 1=备用电源
                })
                
                log_communication(f"成功读取二号板安全状态数据: {registers}")
            else:
                log_communication(f"读取二号板安全状态数据失败: {rr}")
            
            return data
        except Exception as e:
            log_communication(f"读取二号板数据时出错: {str(e)}")
            return None
    
    def read_bms_data(self):
        """读取BMS保护板数据 (地址 0x0100 - 0x010E)"""
        try:
            if not self.client:
                return None
            
            # 读取电池单体电压 (0x0100 - 0x0107)
            rr = self.client.read_holding_registers(0x0100, 8, slave=1)
            if not rr.isError():
                registers = rr.registers
                # 读取系统级参数 (0x0108 - 0x010B)
                rr2 = self.client.read_holding_registers(0x0108, 4, slave=1)
                if not rr2.isError():
                    registers2 = rr2.registers
                    
                    # 读取状态与控制 (0x010C - 0x010E)
                    rr3 = self.client.read_holding_registers(0x010C, 3, slave=1)
                    if not rr3.isError():
                        registers3 = rr3.registers
                        
                        # 处理电流值 (有符号)
                        current_raw = registers2[1]
                        if current_raw >= 32768:
                            current_actual = (current_raw - 65536) / 100.0
                        else:
                            current_actual = current_raw / 100.0
                        
                        data = {
                            # 电池单体电压 (mV)
                            'battery1_voltage': registers[0] / 1000.0,  # 转换为V
                            'battery2_voltage': registers[1] / 1000.0,
                            'battery3_voltage': registers[2] / 1000.0,
                            'battery4_voltage': registers[3] / 1000.0,
                            'battery5_voltage': registers[4] / 1000.0,
                            'battery6_voltage': registers[5] / 1000.0,
                            'battery7_voltage': registers[6] / 1000.0,
                            'battery8_voltage': registers[7] / 1000.0,
                            
                            # 系统级参数
                            'total_voltage': registers2[0] / 1000.0,  # mV转V
                            'current': current_actual,  # A
                            'temperature1': registers2[2] / 10.0,  # ℃
                            'temperature2': registers2[3] / 10.0,  # ℃
                            
                            # 状态与控制
                            'balance_status': registers3[0],  # 1=正在平衡, 0=没有平衡
                            'charge_discharge_status': registers3[1],  # 1=充电, 2=放电, 3=空闲
                            'battery_percentage': registers3[2]  # %
                        }
                        
                        log_communication(f"成功读取BMS数据: 电池电压={registers}, 系统参数={registers2}, 状态={registers3}")
                        return data
                    else:
                        log_communication(f"读取BMS状态数据失败: {rr3}")
                else:
                    log_communication(f"读取BMS系统参数失败: {rr2}")
            else:
                log_communication(f"读取BMS电池电压失败: {rr}")
            
            return None
        except Exception as e:
            log_communication(f"读取BMS数据时出错: {str(e)}")
            return None
    
    def close(self):
        """关闭连接"""
        if self.client:
            self.client.close()
            log_communication("关闭Modbus连接")
            connection_status['connected'] = False
            connection_status['last_check'] = datetime.now().isoformat()

# 创建Modbus读取器实例
modbus_reader = ModbusReader()

# 初始化数据库
init_db()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/management')
def management():
    """数据管理页面"""
    return render_template('management.html')

@app.route('/api/config', methods=['GET', 'POST'])
def config():
    """获取或设置Modbus配置"""
    global modbus_config
    
    if request.method == 'POST':
        data = request.json
        modbus_config['host'] = data.get('host', modbus_config['host'])
        modbus_config['port'] = int(data.get('port', modbus_config['port']))
        return jsonify({'success': True, 'config': modbus_config})
    
    return jsonify(modbus_config)

@app.route('/api/connect', methods=['POST'])
def connect():
    """连接到Modbus服务器"""
    global modbus_config
    data = request.json
    host = data.get('host', modbus_config['host'])
    port = int(data.get('port', modbus_config['port']))
    
    success = modbus_reader.connect(host, port)
    if success:
        modbus_config['host'] = host
        modbus_config['port'] = port
    
    return jsonify({'success': success})

@app.route('/api/disconnect', methods=['POST'])
def disconnect():
    """断开Modbus服务器连接"""
    modbus_reader.close()
    return jsonify({'success': True})

@app.route('/api/connection-status')
def get_connection_status():
    """获取连接状态"""
    # 实时检查连接状态
    is_connected = modbus_reader.is_connected()
    return jsonify({
        'connected': is_connected,
        'last_check': connection_status['last_check']
    })

@app.route('/api/data')
def get_data():
    """获取所有数据"""
    # 检查连接状态
    if not modbus_reader.is_connected():
        return jsonify({
            'error': '未连接到服务器',
            'connected': False
        }), 400
        
    board_data = modbus_reader.read_board_data()
    bms_data = modbus_reader.read_bms_data()
    
    return jsonify({
        'board_data': board_data,
        'bms_data': bms_data,
        'timestamp': datetime.now().isoformat(),
        'connected': True
    })

@app.route('/api/start-recording', methods=['POST'])
def start_recording():
    """开始数据记录"""
    global recording_status
    
    if not modbus_reader.is_connected():
        return jsonify({'success': False, 'error': '未连接到服务器'}), 400
    
    # 生成记录ID
    recording_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    recording_name = request.json.get('name', f'记录_{recording_id}')
    
    try:
        # 保存记录会话信息
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO recording_sessions (id, name, start_time) VALUES (?, ?, ?)',
            (recording_id, recording_name, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        
        # 更新记录状态
        recording_status['is_recording'] = True
        recording_status['recording_id'] = recording_id
        
        log_communication(f"开始数据记录: {recording_name} (ID: {recording_id})")
        
        return jsonify({
            'success': True,
            'recording_id': recording_id,
            'recording_name': recording_name
        })
    except Exception as e:
        log_communication(f"开始记录时出错: {str(e)}")
        return jsonify({'success': False, 'error': f'开始记录时出错: {str(e)}'}), 500

@app.route('/api/stop-recording', methods=['POST'])
def stop_recording():
    """停止数据记录"""
    global recording_status
    
    if not recording_status['is_recording']:
        return jsonify({'success': False, 'error': '未在记录状态'}), 400
    
    try:
        # 更新记录会话结束时间
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE recording_sessions SET end_time = ? WHERE id = ?',
            (datetime.now().isoformat(), recording_status['recording_id'])
        )
        conn.commit()
        conn.close()
        
        # 更新记录状态
        recording_id = recording_status['recording_id']
        recording_status['is_recording'] = False
        recording_status['recording_id'] = None
        
        log_communication(f"停止数据记录: ID {recording_id}")
        
        return jsonify({'success': True, 'recording_id': recording_id})
    except Exception as e:
        log_communication(f"停止记录时出错: {str(e)}")
        return jsonify({'success': False, 'error': f'停止记录时出错: {str(e)}'}), 500

@app.route('/api/save-data', methods=['POST'])
def save_data():
    """保存当前数据到数据库"""
    global recording_status
    
    if not recording_status['is_recording']:
        return jsonify({'success': False, 'error': '未在记录状态'}), 400
    
    # 获取当前数据
    board_data = modbus_reader.read_board_data()
    bms_data = modbus_reader.read_bms_data()
    
    if not board_data or not bms_data:
        return jsonify({'success': False, 'error': '读取数据失败'}), 400
    
    try:
        # 保存数据到数据库
        conn = sqlite3.connect(DB_FILE)
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
            recording_status['recording_id'],
            datetime.now().isoformat(),
            board_data['IN1_current'], board_data['IN1_voltage'],
            board_data['IN2_current'], board_data['IN2_voltage'],
            board_data['IN3_current'], board_data['IN3_voltage'],
            board_data['IN4_current'], board_data['IN4_voltage'],
            board_data['IN5_current'], board_data['IN5_voltage'],
            board_data['IN6_current'], board_data['IN6_voltage'],
            board_data['IN7_current'], board_data['IN7_voltage'],
            board_data['IN8_current'], board_data['IN8_voltage'],
            board_data['IN9_current'], board_data['IN9_voltage'],
            board_data['IN10_current'], board_data['IN10_voltage'],
            board_data['AC_current'], board_data['VBAT_voltage'],
            board_data['temperature_value'], board_data['humidity'],
            board_data['door_status'], board_data['water_status'], board_data['ac_status'],
            bms_data['battery1_voltage'], bms_data['battery2_voltage'],
            bms_data['battery3_voltage'], bms_data['battery4_voltage'],
            bms_data['battery5_voltage'], bms_data['battery6_voltage'],
            bms_data['battery7_voltage'], bms_data['battery8_voltage'],
            bms_data['total_voltage'], bms_data['current'],
            bms_data['temperature1'], bms_data['temperature2'],
            bms_data['balance_status'], bms_data['charge_discharge_status'],
            bms_data['battery_percentage']
        ))
        
        conn.commit()
        conn.close()
        
        log_communication(f"保存数据记录: ID {recording_status['recording_id']}")
        return jsonify({'success': True})
    except Exception as e:
        log_communication(f"保存数据时出错: {str(e)}")
        return jsonify({'success': False, 'error': f'保存数据时出错: {str(e)}'}), 500

@app.route('/api/recordings')
def get_recordings():
    """获取所有记录会话"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, start_time, end_time FROM recording_sessions ORDER BY start_time DESC')
    recordings = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'id': row[0],
        'name': row[1],
        'start_time': row[2],
        'end_time': row[3]
    } for row in recordings])

@app.route('/api/recording/<recording_id>')
def get_recording_data(recording_id):
    """获取指定记录会话的数据"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM data_records WHERE recording_id = ? ORDER BY timestamp', (recording_id,))
        data = cursor.fetchall()
        conn.close()
        
        # 获取列名
        column_names = [description[0] for description in cursor.description]
        
        # 转换为字典列表
        result = []
        for row in data:
            row_dict = dict(zip(column_names, row))
            result.append(row_dict)
        
        return jsonify(result)
    except Exception as e:
        log_communication(f"获取记录数据时出错: {str(e)}")
        return jsonify({'error': f'获取记录数据时出错: {str(e)}'}), 500

@app.route('/api/delete-recording/<recording_id>', methods=['DELETE'])
def delete_recording(recording_id):
    """删除指定记录会话"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 删除数据记录
    cursor.execute('DELETE FROM data_records WHERE recording_id = ?', (recording_id,))
    
    # 删除记录会话
    cursor.execute('DELETE FROM recording_sessions WHERE id = ?', (recording_id,))
    
    conn.commit()
    conn.close()
    
    log_communication(f"删除数据记录: ID {recording_id}")
    
    return jsonify({'success': True})

@app.route('/api/logs')
def get_logs():
    """获取通信日志"""
    return jsonify(communication_log)

@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    """清除通信日志"""
    global communication_log
    communication_log = []
    log_communication("通信日志已清除")
    return jsonify({'success': True})

@app.route('/api/refresh')
def refresh_data():
    """手动刷新数据"""
    return get_data()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)