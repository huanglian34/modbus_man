"""
Modbus设备扫描模块
提供网络扫描功能，用于发现Modbus TCP设备
"""

import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pymodbus.client import ModbusTcpClient
from PyQt5.QtCore import QObject, pyqtSignal, QThread


class DeviceScanner(QObject):
    """设备扫描器类"""
    
    # 定义信号
    device_found = pyqtSignal(str, int)  # 发现设备信号 (IP, 端口)
    scan_progress = pyqtSignal(int, int)  # 扫描进度信号 (当前, 总数)
    scan_finished = pyqtSignal(list)  # 扫描完成信号 (设备列表)
    scan_error = pyqtSignal(str)  # 扫描错误信号 (错误信息)
    log_message = pyqtSignal(str)  # 日志消息信号 (消息)
    
    def __init__(self):
        super().__init__()
        self.is_scanning = False
        self.found_devices = []
        self.found_devices_set = set()  # 用于过滤重复设备
        
    def scan_network(self, base_ip, port=502, timeout=1.0, ip_range=(1, 255), max_workers=50):
        """
        扫描网络中的Modbus设备（使用多线程并发扫描）
        
        Args:
            base_ip (str): 基础IP地址 (如: 192.168.1.1)
            port (int): 端口号，默认502
            timeout (float): 连接超时时间，默认1.0秒
            ip_range (tuple): IP范围 (start, end)，默认(1, 255)
            max_workers (int): 最大并发线程数，默认50
        """
        if self.is_scanning:
            self.log_message.emit("扫描已在进行中...")
            return
            
        self.is_scanning = True
        self.found_devices = []
        self.found_devices_set = set()  # 重置设备集合
        
        try:
            # 提取基础IP地址段
            ip_parts = base_ip.split('.')
            if len(ip_parts) != 4:
                self.log_message.emit('无效的IP地址格式')
                self.is_scanning = False
                return
                
            base_ip_prefix = '.'.join(ip_parts[:3])
            
            start_ip, end_ip = ip_range
            total_ips = end_ip - start_ip + 1
            scanned_count = 0
            
            self.log_message.emit(f'开始扫描网络 {base_ip_prefix}.{start_ip}-{end_ip}:{port}，使用 {max_workers} 个并发线程')
            
            # 生成IP地址列表
            ip_list = [f"{base_ip_prefix}.{i}" for i in range(start_ip, end_ip + 1)]
            
            # 使用线程池并发扫描
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有扫描任务
                future_to_ip = {executor.submit(self._scan_single_device, ip, port, timeout): ip for ip in ip_list}
                
                # 处理完成的任务
                for future in as_completed(future_to_ip):
                    if not self.is_scanning:  # 检查是否被中断
                        break
                        
                    ip = future_to_ip[future]
                    scanned_count += 1
                    
                    # 发出进度信号
                    self.scan_progress.emit(scanned_count, total_ips)
                    
                    try:
                        result = future.result()
                        if result:
                            device_key = f"{result[0]}:{result[1]}"
                            # 检查是否已经发现过该设备
                            if device_key not in self.found_devices_set:
                                self.found_devices_set.add(device_key)
                                device_info = result
                                self.found_devices.append(device_info)
                                self.device_found.emit(result[0], result[1])
                                self.log_message.emit(f'发现Modbus设备: {result[0]}:{result[1]}')
                    except Exception as e:
                        # 记录单个IP扫描的错误
                        self.log_message.emit(f'扫描 {ip} 时出错: {str(e)}')
            
            self.is_scanning = False
            self.scan_finished.emit(self.found_devices)
            self.log_message.emit(f'设备扫描完成，共发现 {len(self.found_devices)} 个设备')
            
        except Exception as e:
            self.is_scanning = False
            error_msg = f'设备扫描出错: {str(e)}'
            self.log_message.emit(error_msg)
            self.scan_error.emit(error_msg)
    
    def _scan_single_device(self, ip, port, timeout):
        """
        扫描单个设备
        
        Args:
            ip (str): IP地址
            port (int): 端口号
            timeout (float): 连接超时时间
            
        Returns:
            tuple or None: (ip, port) 如果是Modbus设备，否则None
        """
        try:
            # 尝试连接到设备
            client = ModbusTcpClient(ip, port, timeout=timeout)
            if client.connect():
                # 尝试读取一些寄存器来验证是否为Modbus设备
                try:
                    rr = client.read_holding_registers(0x0000, 1, slave=1)
                    if not rr.isError():
                        client.close()
                        return (ip, port)
                except Exception:
                    client.close()
                    return None
                client.close()
            return None
        except Exception:
            if 'client' in locals():
                client.close()
            return None
    
    def stop_scan(self):
        """停止扫描"""
        self.is_scanning = False
        self.log_message.emit('扫描已停止')


class ScannerThread(QThread):
    """扫描线程类"""
    
    def __init__(self, scanner, base_ip, port=502, timeout=1.0, ip_range=(1, 255), max_workers=50):
        super().__init__()
        self.scanner = scanner
        self.base_ip = base_ip
        self.port = port
        self.timeout = timeout
        self.ip_range = ip_range
        self.max_workers = max_workers
        
    def run(self):
        self.scanner.scan_network(self.base_ip, self.port, self.timeout, self.ip_range, self.max_workers)
        
    def stop(self):
        self.scanner.stop_scan()