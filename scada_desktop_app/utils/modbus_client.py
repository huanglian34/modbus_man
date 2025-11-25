#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModbusClient:
    def __init__(self):
        self.client = None
        self.connected = False
        
    def connect(self, host, port=502):
        """连接到Modbus TCP服务器"""
        try:
            self.client = ModbusTcpClient(host, port)
            self.client.connect()
            
            if self.client.is_socket_open():
                self.connected = True
                logger.info(f"成功连接到Modbus服务器 {host}:{port}")
                return True
            else:
                self.connected = False
                logger.error(f"无法连接到Modbus服务器 {host}:{port}")
                return False
        except Exception as e:
            self.connected = False
            logger.error(f"连接Modbus服务器时出错: {str(e)}")
            return False
    
    def disconnect(self):
        """断开与Modbus TCP服务器的连接"""
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("已断开Modbus连接")
    
    def read_board_data(self):
        """读取二号板数据"""
        try:
            if not self.client or not self.connected:
                return None
            
            # 读取电源监测数据 (IN1-IN10) (0x0000 - 0x0015)
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
                    
                    # 环境监测数据和安全状态将在后续读取中填充
                    'temperature_sign': None,
                    'temperature_value': None,
                    'humidity': None,
                    'door_status': None,
                    'water_status': None,
                    'ac_status': None
                }
                
                logger.info(f"成功读取二号板电源监测数据")
            else:
                logger.error(f"读取二号板电源监测数据失败: {rr}")
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
                
                logger.info(f"成功读取二号板环境监测数据")
            else:
                logger.error(f"读取二号板环境监测数据失败: {rr}")
            
            # 读取安全状态 (0x0019 - 0x001B)
            rr = self.client.read_holding_registers(0x0019, 3, slave=1)
            if not rr.isError():
                registers = rr.registers
                data.update({
                    'door_status': registers[0],  # 1=打开, 0=关闭
                    'water_status': registers[1],  # 1=有水, 0=没水
                    'ac_status': registers[2]  # 0=主电源, 1=备用电源
                })
                
                logger.info(f"成功读取二号板安全状态数据")
            else:
                logger.error(f"读取二号板安全状态数据失败: {rr}")
            
            return data
        except Exception as e:
            logger.error(f"读取二号板数据时出错: {str(e)}")
            return None
    
    def read_bms_data(self):
        """读取BMS保护板数据"""
        try:
            if not self.client or not self.connected:
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
                            # 电池单体电压 (V)
                            'battery1_voltage': registers[0] / 1000.0,
                            'battery2_voltage': registers[1] / 1000.0,
                            'battery3_voltage': registers[2] / 1000.0,
                            'battery4_voltage': registers[3] / 1000.0,
                            'battery5_voltage': registers[4] / 1000.0,
                            'battery6_voltage': registers[5] / 1000.0,
                            'battery7_voltage': registers[6] / 1000.0,
                            'battery8_voltage': registers[7] / 1000.0,
                            
                            # 系统级参数
                            'total_voltage': registers2[0] / 1000.0,  # V
                            'current': current_actual,  # A
                            'temperature1': registers2[2] / 10.0,  # ℃
                            'temperature2': registers2[3] / 10.0,  # ℃
                            
                            # 状态与控制
                            'balance_status': registers3[0],  # 1=正在平衡, 0=没有平衡
                            'charge_discharge_status': registers3[1],  # 1=充电, 2=放电, 3=空闲
                            'battery_percentage': registers3[2]  # %
                        }
                        
                        logger.info(f"成功读取BMS数据")
                        return data
                    else:
                        logger.error(f"读取BMS状态数据失败: {rr3}")
                else:
                    logger.error(f"读取BMS系统参数失败: {rr2}")
            else:
                logger.error(f"读取BMS电池电压失败: {rr}")
            
            return None
        except Exception as e:
            logger.error(f"读取BMS数据时出错: {str(e)}")
            return None