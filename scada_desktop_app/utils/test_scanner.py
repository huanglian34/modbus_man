#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
扫描模块测试脚本
用于测试DeviceScanner类的功能
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.scanner import DeviceScanner
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QProgressBar
from PyQt5.QtCore import Qt


class ScannerTestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.scanner = DeviceScanner()
        self.init_ui()
        self.connect_signals()
        
    def init_ui(self):
        self.setWindowTitle('设备扫描测试')
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()
        
        self.start_button = QPushButton('开始扫描')
        self.start_button.clicked.connect(self.start_scan)
        layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton('停止扫描')
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)
        
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        self.setLayout(layout)
        
    def connect_signals(self):
        self.scanner.device_found.connect(self.on_device_found)
        self.scanner.scan_progress.connect(self.on_scan_progress)
        self.scanner.scan_finished.connect(self.on_scan_finished)
        self.scanner.scan_error.connect(self.on_scan_error)
        self.scanner.log_message.connect(self.on_log_message)
        
    def start_scan(self):
        base_ip = "192.168.1.1"  # 测试IP地址
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)
        
        # 开始扫描，使用20个并发线程
        self.scanner.scan_network(base_ip, 502, 1.0, (1, 50), 20)
        
    def stop_scan(self):
        self.scanner.stop_scan()
        
    def on_device_found(self, ip, port):
        self.log_text.append(f"[发现设备] {ip}:{port}")
        
    def on_scan_progress(self, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        
    def on_scan_finished(self, devices):
        self.log_text.append(f"[扫描完成] 共发现 {len(devices)} 个设备")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
    def on_scan_error(self, error_msg):
        self.log_text.append(f"[扫描错误] {error_msg}")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
    def on_log_message(self, message):
        timestamp = time.strftime('%H:%M:%S')
        self.log_text.append(f"[{timestamp}] {message}")


def main():
    app = QApplication(sys.argv)
    window = ScannerTestWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()