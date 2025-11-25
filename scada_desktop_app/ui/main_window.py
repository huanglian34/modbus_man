#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QGroupBox, QFrame,
    QTableWidget, QTableWidgetItem, QStatusBar, QToolBar,
    QAction, QTabWidget, QComboBox, QSpinBox, QTextEdit,
    QProgressBar, QMessageBox, QFileDialog, QApplication,
    QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QDateTime
from PyQt5.QtGui import QFont, QIcon, QColor, QScreen

from utils.modbus_client import ModbusClient
from utils.database import DatabaseManager
from utils.scanner import DeviceScanner, ScannerThread

class SCADAMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.modbus_client = ModbusClient()
        self.db_manager = DatabaseManager()
        self.is_connected = False
        self.is_recording = False
        self.recording_id = None
        self.auto_refresh_timer = QTimer()
        
        # 扫描相关属性
        self.scanner = DeviceScanner()
        self.scan_thread = None
        self.found_devices_set = set()  # 用于过滤重复设备
        
        # 获取屏幕信息用于自适应调整
        self.screen = QApplication.primaryScreen()
        self.screen_geometry = self.screen.availableGeometry()
        self.screen_width = self.screen_geometry.width()
        self.screen_height = self.screen_geometry.height()
        
        # 根据屏幕分辨率设置缩放因子
        self.scale_factor = self.calculate_scale_factor()
        
        self.init_ui()
        self.setup_connections()
        self.setup_timers()
        
        # 初始化状态标签
        self.update_auto_refresh_status(False)
        self.update_recording_status(False)
        
        # 连接屏幕变化信号
        QApplication.instance().screenAdded.connect(self.on_screen_changed)
        QApplication.instance().screenRemoved.connect(self.on_screen_changed)
        
        # 连接扫描器信号
        self.connect_scanner_signals()
        self.connect_scanner_signals()
        self.connect_scanner_signals()

        
        # 连接扫描器信号
        self.connect_scanner_signals()
        
    def update_auto_refresh_status(self, is_active):
        """更新自动刷新状态标签显示"""
        if is_active:
            self.auto_refresh_status_label.setText('自动刷新: 运行中')
            self.auto_refresh_status_label.setStyleSheet("QLabel { color: #27ae60; font-weight: bold; padding: 0 10px; }")
        else:
            self.auto_refresh_status_label.setText('自动刷新: 已停止')
            self.auto_refresh_status_label.setStyleSheet("QLabel { color: #95a5a6; font-weight: normal; padding: 0 10px; }")
            
    def update_recording_status(self, is_active, recording_name=None):
        """更新记录状态标签显示"""
        if is_active and recording_name:
            self.recording_status_label.setText(f'记录: {recording_name}')
            self.recording_status_label.setStyleSheet("QLabel { color: #27ae60; font-weight: bold; padding: 0 10px; }")
        else:
            self.recording_status_label.setText('记录: 未记录')
            self.recording_status_label.setStyleSheet("QLabel { color: #95a5a6; font-weight: normal; padding: 0 10px; }")
            
    def connect_scanner_signals(self):
        """连接扫描器信号"""
        self.scanner.device_found.connect(self.on_device_found)
        self.scanner.scan_progress.connect(self.on_scan_progress)
        self.scanner.scan_finished.connect(self.on_scan_finished)
        self.scanner.scan_error.connect(self.on_scan_error)
        self.scanner.log_message.connect(self.on_scan_log_message)
        
    def calculate_scale_factor(self):
        """根据屏幕分辨率计算缩放因子"""
        # 基准分辨率1920x1080
        base_width = 1920
        base_height = 1080
        
        # 计算缩放因子
        width_factor = self.screen_width / base_width
        height_factor = self.screen_height / base_height
        
        # 对于1080p屏幕，使用更合适的缩放因子
        if self.screen_width == 1920 and self.screen_height == 1080:
            return 1.0
        
        # 取较小的因子以确保界面在所有屏幕上都能完整显示
        scale_factor = min(width_factor, height_factor)
        
        # 限制缩放因子范围
        scale_factor = max(0.7, min(1.5, scale_factor))
        
        return scale_factor
        
    def on_screen_changed(self, screen):
        """屏幕变化时的处理函数"""
        # 重新获取屏幕信息
        self.screen = QApplication.primaryScreen()
        self.screen_geometry = self.screen.availableGeometry()
        self.screen_width = self.screen_geometry.width()
        self.screen_height = self.screen_geometry.height()
        
        # 重新计算缩放因子
        self.scale_factor = self.calculate_scale_factor()
        
        # 重新应用样式和布局
        self.apply_scaled_styles()
        self.adjust_layout_for_scale()
        
    def init_ui(self):
        self.setWindowTitle('斯络通上位机监控系统')
        
        # 应用缩放样式
        self.apply_scaled_styles()
        
        # 根据屏幕分辨率调整窗口大小
        self.adjust_layout_for_scale()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(int(15 * self.scale_factor))
        main_layout.setContentsMargins(
            int(20 * self.scale_factor),
            int(20 * self.scale_factor),
            int(20 * self.scale_factor),
            int(20 * self.scale_factor)
        )
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 创建各个标签页
        self.create_connection_tab()
        self.create_control_tab()
        self.create_board_data_tab()
        self.create_bms_data_tab()
        self.create_chart_tab()
        self.create_log_tab()
        self.create_recordings_tab()
        
        # 创建状态栏
        self.create_status_bar()
        
        # 设置初始状态
        self.update_connection_status(False)
        
    def add_scan_result(self, ip, port):
        row = self.scan_results.rowCount()
        self.scan_results.insertRow(row)
        
        # 设置表格项字体和颜色
        ip_item = QTableWidgetItem(ip)
        ip_item.setFont(QFont("Microsoft YaHei", int(14 * self.scale_factor)))
        ip_item.setForeground(QColor("#222222"))
        self.scan_results.setItem(row, 0, ip_item)
        
        port_item = QTableWidgetItem(str(port))
        port_item.setFont(QFont("Microsoft YaHei", int(14 * self.scale_factor)))
        port_item.setForeground(QColor("#222222"))
        self.scan_results.setItem(row, 1, port_item)
        
        # 创建选择按钮并设置样式
        select_button = QPushButton('选择')
        select_button.setFont(QFont("Microsoft YaHei", int(14 * self.scale_factor)))
        select_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: {int(5 * self.scale_factor)}px {int(10 * self.scale_factor)}px;
                border-radius: {int(5 * self.scale_factor)}px;
                font-size: {int(14 * self.scale_factor)}px;
                font-weight: 500;
                font-family: "Microsoft YaHei";
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
            QPushButton:pressed {{
                background-color: #3d8b40;
            }}
        """)
        select_button.clicked.connect(lambda: self.select_device(ip, port))
        self.scan_results.setCellWidget(row, 2, select_button)
        
        # 调整行高以适应按钮
        self.scan_results.setRowHeight(row, int(40 * self.scale_factor))
        
    def apply_scaled_styles(self):
        """根据缩放因子应用样式"""
        # 计算缩放后的字体大小
        title_font_size = int(24 * self.scale_factor)
        group_title_font_size = int(18 * self.scale_factor)
        label_font_size = int(16 * self.scale_factor)
        data_label_font_size = int(17 * self.scale_factor)
        data_value_font_size = int(18 * self.scale_factor)
        button_font_size = int(16 * self.scale_factor)
        status_font_size = int(15 * self.scale_factor)
        
        # 应用缩放后的样式，使用微软雅黑字体
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #f5f5f5;
                font-family: "Microsoft YaHei", Arial, sans-serif;
            }}
            
            QToolBar {{
                background-color: #ffffff;
                border: none;
                padding: {int(10 * self.scale_factor)}px;
                spacing: {int(15 * self.scale_factor)}px;
            }}
            
            QToolBar QToolButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: {int(5 * self.scale_factor)}px;
                padding: {int(8 * self.scale_factor)}px {int(12 * self.scale_factor)}px;
                font-size: {button_font_size}px;
                font-weight: 500;
                color: #222222;
                font-family: "Microsoft YaHei";
            }}
            
            QToolBar QToolButton:hover {{
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
            }}
            
            QToolBar QToolButton:pressed {{
                background-color: #e0e0e0;
            }}
            
            QTabWidget::pane {{
                border: 1px solid #d0d0d0;
                border-radius: {int(8 * self.scale_factor)}px;
                background-color: #ffffff;
            }}
            
            QTabBar::tab {{
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-bottom: none;
                border-top-left-radius: {int(6 * self.scale_factor)}px;
                border-top-right-radius: {int(6 * self.scale_factor)}px;
                padding: {int(10 * self.scale_factor)}px {int(20 * self.scale_factor)}px;
                margin-right: {int(2 * self.scale_factor)}px;
                font-size: {int(16 * self.scale_factor)}px;
                font-weight: 500;
                color: #444444;
                font-family: "Microsoft YaHei";
            }}
            
            QTabBar::tab:selected {{
                background-color: #ffffff;
                color: #222222;
                font-weight: 600;
            }}
            
            QTabBar::tab:!selected:hover {{
                background-color: #e8e8e8;
            }}
            
            QGroupBox {{
                border: 1px solid #d0d0d0;
                border-radius: {int(8 * self.scale_factor)}px;
                margin-top: {int(15 * self.scale_factor)}px;
                background-color: #ffffff;
                font-family: "Microsoft YaHei";
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: {int(15 * self.scale_factor)}px;
                padding: 0 {int(5 * self.scale_factor)}px;
                font-size: {group_title_font_size}px;
                font-weight: 600;
                color: #222222;
                background-color: #ffffff;
            }}
            
            QLabel {{
                color: #222222;
                font-size: {label_font_size}px;
                font-family: "Microsoft YaHei";
            }}
            
            QLabel#data_label {{
                font-size: {data_label_font_size}px;
                font-weight: 500;
                color: #555555;
            }}
            
            QLabel#data_value {{
                font-size: {data_value_font_size}px;
                font-weight: 600;
                color: #1a73e8;
                background-color: #f8f9fa;
                padding: {int(5 * self.scale_factor)}px {int(10 * self.scale_factor)}px;
                border-radius: {int(5 * self.scale_factor)}px;
                border: 1px solid #e0e0e0;
            }}
            
            QPushButton {{
                background-color: #1a73e8;
                color: white;
                border: none;
                padding: {int(8 * self.scale_factor)}px {int(16 * self.scale_factor)}px;
                border-radius: {int(6 * self.scale_factor)}px;
                font-size: {button_font_size}px;
                font-weight: 500;
                min-height: {int(30 * self.scale_factor)}px;
                font-family: "Microsoft YaHei";
            }}
            
            QPushButton:hover {{
                background-color: #0d62d0;
            }}
            
            QPushButton:pressed {{
                background-color: #0a50b0;
            }}
            
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
            }}
            
            QLineEdit {{
                padding: {int(8 * self.scale_factor)}px {int(12 * self.scale_factor)}px;
                border: 1px solid #d0d0d0;
                border-radius: {int(5 * self.scale_factor)}px;
                background-color: #ffffff;
                font-size: {label_font_size}px;
                font-weight: 500;
                selection-background-color: #d2e3fc;
                font-family: "Microsoft YaHei";
            }}
            
            QLineEdit:focus {{
                border: 1px solid #1a73e8;
                outline: none;
            }}
            
            QSpinBox {{
                padding: {int(6 * self.scale_factor)}px;
                border: 1px solid #d0d0d0;
                border-radius: {int(5 * self.scale_factor)}px;
                background-color: #ffffff;
                font-size: {label_font_size}px;
                font-weight: 500;
                font-family: "Microsoft YaHei";
            }}
            
            QSpinBox:focus {{
                border: 1px solid #1a73e8;
            }}
            
            QTableWidget {{
                background-color: #ffffff;
                alternate-background-color: #f8f8f8;
                selection-background-color: #d2e3fc;
                selection-color: #222222;
                gridline-color: #eeeeee;
                border: 1px solid #d0d0d0;
                border-radius: {int(5 * self.scale_factor)}px;
                font-size: {int(15 * self.scale_factor)}px;
                font-family: "Microsoft YaHei";
            }}
            
            QHeaderView::section {{
                background-color: #f0f0f0;
                color: #222222;
                padding: {int(10 * self.scale_factor)}px;
                border: none;
                font-weight: 600;
                font-size: {int(16 * self.scale_factor)}px;
                font-family: "Microsoft YaHei";
            }}
            
            QProgressBar {{
                border: 1px solid #d0d0d0;
                border-radius: {int(5 * self.scale_factor)}px;
                background-color: #f0f0f0;
                text-align: center;
                height: {int(18 * self.scale_factor)}px;
            }}
            
            QProgressBar::chunk {{
                background-color: #1a73e8;
                border-radius: {int(4 * self.scale_factor)}px;
            }}
            
            QStatusBar {{
                background-color: #ffffff;
                border-top: 1px solid #d0d0d0;
                color: #666666;
                font-size: {status_font_size}px;
                font-weight: 500;
                padding: {int(6 * self.scale_factor)}px {int(15 * self.scale_factor)}px;
                font-family: "Microsoft YaHei";
            }}
            
            QTextEdit {{
                font-family: "Microsoft YaHei";
                font-size: {int(14 * self.scale_factor)}px;
            }}
            
            QComboBox {{
                font-family: "Microsoft YaHei";
                font-size: {label_font_size}px;
                padding: {int(6 * self.scale_factor)}px;
            }}
        """)
        
    def adjust_layout_for_scale(self):
        """根据缩放因子调整布局"""
        # 调整主窗口大小
        base_width = 1000
        base_height = 700
        scaled_width = int(base_width * self.scale_factor)
        scaled_height = int(base_height * self.scale_factor)
        
        # 对于1080p屏幕，使用固定大小以确保最佳显示效果
        if self.screen_width == 1920 and self.screen_height == 1080:
            scaled_width = 1000
            scaled_height = 700
        else:
            # 确保窗口大小在合理范围内
            scaled_width = max(800, min(1920, scaled_width))
            scaled_height = max(600, min(900, scaled_height))
        
        self.resize(scaled_width, scaled_height)
        
        # 将窗口居中显示
        self.center_window_on_screen()
        
        # 调整布局间距
        main_widget = self.centralWidget()
        if main_widget and main_widget.layout():
            layout = main_widget.layout()
            layout.setSpacing(int(15 * self.scale_factor))
            layout.setContentsMargins(
                int(20 * self.scale_factor),
                int(20 * self.scale_factor),
                int(20 * self.scale_factor),
                int(20 * self.scale_factor)
            )
            
    def center_window_on_screen(self):
        """将窗口居中显示在屏幕中央"""
        # 获取屏幕可用区域
        screen_geometry = self.screen.availableGeometry()
        screen_center = screen_geometry.center()
        
        # 计算窗口左上角坐标以使其居中
        window_frame = self.frameGeometry()
        window_frame.moveCenter(screen_center)
        
        # 确保窗口不会超出屏幕边界
        x = max(screen_geometry.left(), min(window_frame.x(), screen_geometry.right() - self.width()))
        y = max(screen_geometry.top(), min(window_frame.y(), screen_geometry.bottom() - self.height()))
        
        self.move(x, y - 200)
        
    def create_toolbar(self):
        toolbar = self.addToolBar('主工具栏')
        
        # 连接按钮
        self.connect_action = QAction('连接', self)
        self.connect_action.triggered.connect(self.toggle_connection)
        toolbar.addAction(self.connect_action)
        
        # 刷新按钮
        self.refresh_action = QAction('刷新', self)
        self.refresh_action.triggered.connect(self.refresh_data)
        toolbar.addAction(self.refresh_action)
        
        # 自动刷新按钮
        self.auto_refresh_action = QAction('自动刷新', self)
        self.auto_refresh_action.triggered.connect(self.toggle_auto_refresh)
        toolbar.addAction(self.auto_refresh_action)
        
        # 开始记录按钮
        self.start_record_action = QAction('开始记录', self)
        self.start_record_action.triggered.connect(self.start_recording)
        self.start_record_action.setEnabled(False)
        toolbar.addAction(self.start_record_action)
        
        # 停止记录按钮
        self.stop_record_action = QAction('停止记录', self)
        self.stop_record_action.triggered.connect(self.stop_recording)
        self.stop_record_action.setEnabled(False)
        toolbar.addAction(self.stop_record_action)
        
    def create_connection_tab(self):
        connection_tab = QWidget()
        layout = QVBoxLayout(connection_tab)
        layout.setSpacing(int(10 * self.scale_factor))
        
        # 连接配置组
        config_group = QGroupBox('连接配置')
        config_layout = QGridLayout(config_group)
        config_layout.setSpacing(int(10 * self.scale_factor))
        config_layout.setContentsMargins(
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor)
        )
        
        # IP地址
        ip_label = QLabel('服务器IP:')
        ip_label.setStyleSheet(f"font-size: {int(16 * self.scale_factor)}px; font-family: 'Microsoft YaHei';")
        config_layout.addWidget(ip_label, 0, 0)
        self.ip_input = QLineEdit('192.168.1.10')
        self.ip_input.setStyleSheet(f"font-size: {int(16 * self.scale_factor)}px; font-family: 'Microsoft YaHei';")
        config_layout.addWidget(self.ip_input, 0, 1)
        
        # 端口
        port_label = QLabel('端口:')
        port_label.setStyleSheet(f"font-size: {int(16 * self.scale_factor)}px; font-family: 'Microsoft YaHei';")
        config_layout.addWidget(port_label, 0, 2)
        self.port_input = QLineEdit('502')
        self.port_input.setFixedWidth(int(100 * self.scale_factor))
        self.port_input.setStyleSheet(f"font-size: {int(16 * self.scale_factor)}px; font-family: 'Microsoft YaHei';")
        config_layout.addWidget(self.port_input, 0, 3)
        
        # 连接按钮
        self.connection_button = QPushButton('连接')
        self.connection_button.clicked.connect(self.toggle_connection)
        self.connection_button.setStyleSheet(f"font-size: {int(16 * self.scale_factor)}px; font-family: 'Microsoft YaHei';")
        self.connection_button.setFixedWidth(int(100 * self.scale_factor))
        config_layout.addWidget(self.connection_button, 0, 4)
        
        # 扫描按钮
        self.scan_button = QPushButton('扫描设备')
        self.scan_button.clicked.connect(self.scan_devices)
        self.scan_button.setStyleSheet(f"font-size: {int(16 * self.scale_factor)}px; font-family: 'Microsoft YaHei';")
        self.scan_button.setFixedWidth(int(120 * self.scale_factor))
        config_layout.addWidget(self.scan_button, 0, 5)
        
        # 停止扫描按钮
        self.stop_scan_button = QPushButton('停止扫描')
        self.stop_scan_button.clicked.connect(self.stop_scan)
        self.stop_scan_button.setStyleSheet(f"font-size: {int(16 * self.scale_factor)}px; font-family: 'Microsoft YaHei';")
        self.stop_scan_button.setFixedWidth(int(120 * self.scale_factor))
        self.stop_scan_button.setEnabled(False)
        config_layout.addWidget(self.stop_scan_button, 0, 6)
        
        # 设置列伸缩策略，使IP输入框可以扩展
        config_layout.setColumnStretch(1, 1)
        
        layout.addWidget(config_group)
        
        # 扫描结果
        result_label = QLabel('扫描结果:')
        result_label.setStyleSheet(f"font-size: {int(16 * self.scale_factor)}px; font-weight: 600; font-family: 'Microsoft YaHei';")
        layout.addWidget(result_label)
        
        self.scan_results = QTableWidget(0, 3)
        self.scan_results.setHorizontalHeaderLabels(['IP地址', '端口', '操作'])
        self.scan_results.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.scan_results.setStyleSheet(f"font-size: {int(15 * self.scale_factor)}px; font-family: 'Microsoft YaHei';")
        self.scan_results.horizontalHeader().setStyleSheet(f"font-size: {int(15 * self.scale_factor)}px; font-family: 'Microsoft YaHei'; font-weight: 600;")
        self.scan_results.verticalHeader().setStyleSheet(f"font-size: {int(14 * self.scale_factor)}px; font-family: 'Microsoft YaHei';")
        layout.addWidget(self.scan_results)
        
        # 设置表格列伸缩策略
        self.scan_results.horizontalHeader().setStretchLastSection(True)
        self.scan_results.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.scan_results.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        self.tab_widget.addTab(connection_tab, '连接配置')
        
    def create_control_tab(self):
        control_tab = QWidget()
        layout = QVBoxLayout(control_tab)
        layout.setSpacing(int(15 * self.scale_factor))
        
        # 标题
        title_label = QLabel('系统控制面板')
        title_font_size = int(24 * self.scale_factor)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: {title_font_size}px;
                font-weight: 700;
                color: #222222;
                margin-bottom: {int(12 * self.scale_factor)}px;
            }}
        """)
        layout.addWidget(title_label)
        
        # 控制面板组
        control_group = QGroupBox('控制面板')
        control_layout = QVBoxLayout(control_group)
        control_layout.setSpacing(int(15 * self.scale_factor))
        control_layout.setContentsMargins(
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor)
        )
        
        # 刷新控制区域
        refresh_group = QGroupBox('数据刷新控制')
        refresh_layout = QVBoxLayout(refresh_group)
        refresh_layout.setSpacing(int(10 * self.scale_factor))
        refresh_layout.setContentsMargins(
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor)
        )
        
        # 手动刷新按钮
        manual_refresh_layout = QHBoxLayout()
        self.refresh_button = QPushButton('手动刷新数据')
        self.refresh_button.clicked.connect(self.refresh_data)
        self.refresh_button.setProperty("button-style", "secondary")
        manual_refresh_layout.addWidget(self.refresh_button)
        manual_refresh_layout.addStretch()
        refresh_layout.addLayout(manual_refresh_layout)
        
        # 自动刷新控制
        auto_refresh_layout = QHBoxLayout()
        auto_refresh_layout.addWidget(QLabel('自动刷新间隔(秒):'))
        
        self.refresh_interval = QSpinBox()
        self.refresh_interval.setRange(1, 60)
        self.refresh_interval.setValue(5)
        self.refresh_interval.setFixedWidth(int(80 * self.scale_factor))
        auto_refresh_layout.addWidget(self.refresh_interval)
        
        self.auto_refresh_button = QPushButton('开始自动刷新')
        self.auto_refresh_button.clicked.connect(self.toggle_auto_refresh)
        auto_refresh_layout.addWidget(self.auto_refresh_button)
        auto_refresh_layout.addStretch()
        
        refresh_layout.addLayout(auto_refresh_layout)
        
        control_layout.addWidget(refresh_group)
        
        # 数据记录控制组
        record_group = QGroupBox('数据记录控制')
        record_layout = QVBoxLayout(record_group)
        record_layout.setSpacing(int(15 * self.scale_factor))
        record_layout.setContentsMargins(
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor)
        )
        
        # 记录名称输入
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel('记录名称:'))
        self.record_name_input = QLineEdit()
        self.record_name_input.setPlaceholderText('请输入记录名称')
        name_layout.addWidget(self.record_name_input)
        record_layout.addLayout(name_layout)
        
        # 记录按钮
        record_button_layout = QHBoxLayout()
        self.start_record_button = QPushButton('开始记录数据')
        self.start_record_button.clicked.connect(self.start_recording)
        self.start_record_button.setEnabled(False)
        record_button_layout.addWidget(self.start_record_button)
        
        self.stop_record_button = QPushButton('停止记录数据')
        self.stop_record_button.clicked.connect(self.stop_recording)
        self.stop_record_button.setEnabled(False)
        self.stop_record_button.setProperty("button-style", "danger")
        record_button_layout.addWidget(self.stop_record_button)
        record_button_layout.addStretch()
        
        record_layout.addLayout(record_button_layout)
        
        # 记录状态显示
        self.record_status_label = QLabel('状态: 未记录')
        label_font_size = int(17 * self.scale_factor)
        self.record_status_label.setStyleSheet(f"""
            QLabel {{
                font-weight: 600;
                font-size: {label_font_size}px;
                padding: {int(12 * self.scale_factor)}px;
                background-color: #f8f8f8;
                border-radius: {int(6 * self.scale_factor)}px;
                border-left: {int(4 * self.scale_factor)}px solid #1a73e8;
            }}
        """)
        record_layout.addWidget(self.record_status_label)
        
        control_layout.addWidget(record_group)
        
        # 系统操作组
        system_group = QGroupBox('系统操作')
        system_layout = QVBoxLayout(system_group)
        system_layout.setSpacing(int(10 * self.scale_factor))
        system_layout.setContentsMargins(
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor)
        )
        
        # 系统按钮
        system_button_layout = QHBoxLayout()
        self.refresh_recordings_button = QPushButton('刷新记录列表')
        self.refresh_recordings_button.clicked.connect(self.refresh_recordings)
        system_button_layout.addWidget(self.refresh_recordings_button)
        
        self.clear_log_button = QPushButton('清除通信日志')
        self.clear_log_button.clicked.connect(self.clear_logs)
        system_button_layout.addWidget(self.clear_log_button)
        
        system_button_layout.addStretch()
        system_layout.addLayout(system_button_layout)
        
        control_layout.addWidget(system_group)
        
        layout.addWidget(control_group)
        layout.addStretch()
        
        self.tab_widget.addTab(control_tab, '控制面板')
        
    def create_board_data_tab(self):
        board_tab = QWidget()
        layout = QVBoxLayout(board_tab)
        layout.setSpacing(int(15 * self.scale_factor))
        
        # 标题
        title_label = QLabel('二号板数据监控')
        title_font_size = int(24 * self.scale_factor)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: {title_font_size}px;
                font-weight: 700;
                color: #222222;
                margin-bottom: {int(12 * self.scale_factor)}px;
            }}
        """)
        layout.addWidget(title_label)
        
        # 电源监测数据 (IN1-IN10) - 紧凑网格布局
        power_group = QGroupBox('电源监测 (IN1-IN10)')
        power_layout = QGridLayout(power_group)
        power_layout.setSpacing(int(10 * self.scale_factor))
        power_layout.setContentsMargins(
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor)
        )
        
        # 数据项样式
        label_font_size = int(17 * self.scale_factor)
        value_font_size = int(18 * self.scale_factor)
        data_label_style = f"QLabel {{ font-weight: 600; font-size: {label_font_size}px; color: #555555; }}"
        data_value_style = f"QLabel {{ font-weight: 700; font-size: {value_font_size}px; padding: {int(6 * self.scale_factor)}px {int(10 * self.scale_factor)}px; background-color: #f8f8f8; border-radius: {int(5 * self.scale_factor)}px; }}"
        
        # IN1
        in1_label = QLabel('IN1 电流:')
        in1_label.setStyleSheet(data_label_style)
        power_layout.addWidget(in1_label, 0, 0)
        self.in1_current_label = QLabel('-- mA')
        self.in1_current_label.setStyleSheet(data_value_style + f" QLabel {{ color: #1a73e8; }}")
        power_layout.addWidget(self.in1_current_label, 0, 1)
        
        in1_v_label = QLabel('IN1 电压:')
        in1_v_label.setStyleSheet(data_label_style)
        power_layout.addWidget(in1_v_label, 0, 2)
        self.in1_voltage_label = QLabel('-- V')
        self.in1_voltage_label.setStyleSheet(data_value_style + f" QLabel {{ color: #0d7c4a; }}")
        power_layout.addWidget(self.in1_voltage_label, 0, 3)
        
        # IN2
        in2_label = QLabel('IN2 电流:')
        in2_label.setStyleSheet(data_label_style)
        power_layout.addWidget(in2_label, 1, 0)
        self.in2_current_label = QLabel('-- mA')
        self.in2_current_label.setStyleSheet(data_value_style + f" QLabel {{ color: #1a73e8; }}")
        power_layout.addWidget(self.in2_current_label, 1, 1)
        
        in2_v_label = QLabel('IN2 电压:')
        in2_v_label.setStyleSheet(data_label_style)
        power_layout.addWidget(in2_v_label, 1, 2)
        self.in2_voltage_label = QLabel('-- V')
        self.in2_voltage_label.setStyleSheet(data_value_style + f" QLabel {{ color: #0d7c4a; }}")
        power_layout.addWidget(self.in2_voltage_label, 1, 3)
        
        # IN3
        in3_label = QLabel('IN3 电流:')
        in3_label.setStyleSheet(data_label_style)
        power_layout.addWidget(in3_label, 2, 0)
        self.in3_current_label = QLabel('-- mA')
        self.in3_current_label.setStyleSheet(data_value_style + f" QLabel {{ color: #1a73e8; }}")
        power_layout.addWidget(self.in3_current_label, 2, 1)
        
        in3_v_label = QLabel('IN3 电压:')
        in3_v_label.setStyleSheet(data_label_style)
        power_layout.addWidget(in3_v_label, 2, 2)
        self.in3_voltage_label = QLabel('-- V')
        self.in3_voltage_label.setStyleSheet(data_value_style + f" QLabel {{ color: #0d7c4a; }}")
        power_layout.addWidget(self.in3_voltage_label, 2, 3)
        
        # IN4
        in4_label = QLabel('IN4 电流:')
        in4_label.setStyleSheet(data_label_style)
        power_layout.addWidget(in4_label, 3, 0)
        self.in4_current_label = QLabel('-- mA')
        self.in4_current_label.setStyleSheet(data_value_style + f" QLabel {{ color: #1a73e8; }}")
        power_layout.addWidget(self.in4_current_label, 3, 1)
        
        in4_v_label = QLabel('IN4 电压:')
        in4_v_label.setStyleSheet(data_label_style)
        power_layout.addWidget(in4_v_label, 3, 2)
        self.in4_voltage_label = QLabel('-- V')
        self.in4_voltage_label.setStyleSheet(data_value_style + f" QLabel {{ color: #0d7c4a; }}")
        power_layout.addWidget(self.in4_voltage_label, 3, 3)
        
        # IN5
        in5_label = QLabel('IN5 电流:')
        in5_label.setStyleSheet(data_label_style)
        power_layout.addWidget(in5_label, 4, 0)
        self.in5_current_label = QLabel('-- mA')
        self.in5_current_label.setStyleSheet(data_value_style + f" QLabel {{ color: #1a73e8; }}")
        power_layout.addWidget(self.in5_current_label, 4, 1)
        
        in5_v_label = QLabel('IN5 电压:')
        in5_v_label.setStyleSheet(data_label_style)
        power_layout.addWidget(in5_v_label, 4, 2)
        self.in5_voltage_label = QLabel('-- V')
        self.in5_voltage_label.setStyleSheet(data_value_style + f" QLabel {{ color: #0d7c4a; }}")
        power_layout.addWidget(self.in5_voltage_label, 4, 3)
        
        # IN6
        in6_label = QLabel('IN6 电流:')
        in6_label.setStyleSheet(data_label_style)
        power_layout.addWidget(in6_label, 5, 0)
        self.in6_current_label = QLabel('-- mA')
        self.in6_current_label.setStyleSheet(data_value_style + f" QLabel {{ color: #1a73e8; }}")
        power_layout.addWidget(self.in6_current_label, 5, 1)
        
        in6_v_label = QLabel('IN6 电压:')
        in6_v_label.setStyleSheet(data_label_style)
        power_layout.addWidget(in6_v_label, 5, 2)
        self.in6_voltage_label = QLabel('-- V')
        self.in6_voltage_label.setStyleSheet(data_value_style + f" QLabel {{ color: #0d7c4a; }}")
        power_layout.addWidget(self.in6_voltage_label, 5, 3)
        
        # IN7
        in7_label = QLabel('IN7 电流:')
        in7_label.setStyleSheet(data_label_style)
        power_layout.addWidget(in7_label, 6, 0)
        self.in7_current_label = QLabel('-- mA')
        self.in7_current_label.setStyleSheet(data_value_style + f" QLabel {{ color: #1a73e8; }}")
        power_layout.addWidget(self.in7_current_label, 6, 1)
        
        in7_v_label = QLabel('IN7 电压:')
        in7_v_label.setStyleSheet(data_label_style)
        power_layout.addWidget(in7_v_label, 6, 2)
        self.in7_voltage_label = QLabel('-- V')
        self.in7_voltage_label.setStyleSheet(data_value_style + f" QLabel {{ color: #0d7c4a; }}")
        power_layout.addWidget(self.in7_voltage_label, 6, 3)
        
        # IN8
        in8_label = QLabel('IN8 电流:')
        in8_label.setStyleSheet(data_label_style)
        power_layout.addWidget(in8_label, 7, 0)
        self.in8_current_label = QLabel('-- mA')
        self.in8_current_label.setStyleSheet(data_value_style + f" QLabel {{ color: #1a73e8; }}")
        power_layout.addWidget(self.in8_current_label, 7, 1)
        
        in8_v_label = QLabel('IN8 电压:')
        in8_v_label.setStyleSheet(data_label_style)
        power_layout.addWidget(in8_v_label, 7, 2)
        self.in8_voltage_label = QLabel('-- V')
        self.in8_voltage_label.setStyleSheet(data_value_style + f" QLabel {{ color: #0d7c4a; }}")
        power_layout.addWidget(self.in8_voltage_label, 7, 3)
        
        # IN9
        in9_label = QLabel('IN9 电流:')
        in9_label.setStyleSheet(data_label_style)
        power_layout.addWidget(in9_label, 8, 0)
        self.in9_current_label = QLabel('-- mA')
        self.in9_current_label.setStyleSheet(data_value_style + f" QLabel {{ color: #1a73e8; }}")
        power_layout.addWidget(self.in9_current_label, 8, 1)
        
        in9_v_label = QLabel('IN9 电压:')
        in9_v_label.setStyleSheet(data_label_style)
        power_layout.addWidget(in9_v_label, 8, 2)
        self.in9_voltage_label = QLabel('-- V')
        self.in9_voltage_label.setStyleSheet(data_value_style + f" QLabel {{ color: #0d7c4a; }}")
        power_layout.addWidget(self.in9_voltage_label, 8, 3)
        
        # IN10
        in10_label = QLabel('IN10 电流:')
        in10_label.setStyleSheet(data_label_style)
        power_layout.addWidget(in10_label, 9, 0)
        self.in10_current_label = QLabel('-- mA')
        self.in10_current_label.setStyleSheet(data_value_style + f" QLabel {{ color: #1a73e8; }}")
        power_layout.addWidget(self.in10_current_label, 9, 1)
        
        in10_v_label = QLabel('IN10 电压:')
        in10_v_label.setStyleSheet(data_label_style)
        power_layout.addWidget(in10_v_label, 9, 2)
        self.in10_voltage_label = QLabel('-- V')
        self.in10_voltage_label.setStyleSheet(data_value_style + f" QLabel {{ color: #0d7c4a; }}")
        power_layout.addWidget(self.in10_voltage_label, 9, 3)
        
        # AC和VBAT
        ac_label = QLabel('AC 电流:')
        ac_label.setStyleSheet(data_label_style)
        power_layout.addWidget(ac_label, 10, 0)
        self.ac_current_label = QLabel('-- A')
        self.ac_current_label.setStyleSheet(data_value_style + f" QLabel {{ color: #f9ab00; }}")
        power_layout.addWidget(self.ac_current_label, 10, 1)
        
        vbat_label = QLabel('VBAT 电压:')
        vbat_label.setStyleSheet(data_label_style)
        power_layout.addWidget(vbat_label, 10, 2)
        self.vbat_voltage_label = QLabel('-- V')
        self.vbat_voltage_label.setStyleSheet(data_value_style + f" QLabel {{ color: #9334e6; }}")
        power_layout.addWidget(self.vbat_voltage_label, 10, 3)
        
        layout.addWidget(power_group)
        
        # 环境监测和安全状态 - 水平布局
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setSpacing(int(15 * self.scale_factor))
        
        # 环境监测数据
        env_group = QGroupBox('环境监测')
        env_layout = QGridLayout(env_group)
        env_layout.setSpacing(int(10 * self.scale_factor))
        env_layout.setContentsMargins(
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor)
        )
        
        temp_label = QLabel('温度:')
        temp_label.setStyleSheet(data_label_style)
        env_layout.addWidget(temp_label, 0, 0)
        self.temperature_label = QLabel('-- ℃')
        temp_value_font_size = int(20 * self.scale_factor)
        self.temperature_label.setStyleSheet(data_value_style + f" QLabel {{ color: #ea4335; font-size: {temp_value_font_size}px; }}")
        env_layout.addWidget(self.temperature_label, 0, 1)
        
        humidity_label = QLabel('湿度:')
        humidity_label.setStyleSheet(data_label_style)
        env_layout.addWidget(humidity_label, 1, 0)
        self.humidity_label = QLabel('-- %RH')
        self.humidity_label.setStyleSheet(data_value_style + f" QLabel {{ color: #1da1f2; font-size: {temp_value_font_size}px; }}")
        env_layout.addWidget(self.humidity_label, 1, 1)
        
        bottom_layout.addWidget(env_group)
        
        # 安全状态
        safety_group = QGroupBox('安全状态')
        safety_layout = QGridLayout(safety_group)
        safety_layout.setSpacing(int(10 * self.scale_factor))
        safety_layout.setContentsMargins(
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor)
        )
        
        door_label = QLabel('门状态:')
        door_label.setStyleSheet(data_label_style)
        safety_layout.addWidget(door_label, 0, 0)
        self.door_status_label = QLabel('--')
        self.door_status_label.setStyleSheet(data_value_style + f" QLabel {{ color: #fbbc04; font-size: {temp_value_font_size}px; }}")
        safety_layout.addWidget(self.door_status_label, 0, 1)
        
        water_label = QLabel('水浸状态:')
        water_label.setStyleSheet(data_label_style)
        safety_layout.addWidget(water_label, 1, 0)
        self.water_status_label = QLabel('--')
        self.water_status_label.setStyleSheet(data_value_style + f" QLabel {{ color: #fbbc04; font-size: {temp_value_font_size}px; }}")
        safety_layout.addWidget(self.water_status_label, 1, 1)
        
        ac_s_label = QLabel('AC检测状态:')
        ac_s_label.setStyleSheet(data_label_style)
        safety_layout.addWidget(ac_s_label, 2, 0)
        self.ac_status_label = QLabel('--')
        self.ac_status_label.setStyleSheet(data_value_style + f" QLabel {{ color: #fbbc04; font-size: {temp_value_font_size}px; }}")
        safety_layout.addWidget(self.ac_status_label, 2, 1)
        
        bottom_layout.addWidget(safety_group)
        
        layout.addWidget(bottom_widget)
        
        self.tab_widget.addTab(board_tab, '二号板数据')
        
    def create_bms_data_tab(self):
        bms_tab = QWidget()
        layout = QVBoxLayout(bms_tab)
        layout.setSpacing(int(15 * self.scale_factor))
        
        # 标题
        title_label = QLabel('BMS保护板数据监控')
        title_font_size = int(24 * self.scale_factor)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: {title_font_size}px;
                font-weight: 700;
                color: #222222;
                margin-bottom: {int(12 * self.scale_factor)}px;
            }}
        """)
        layout.addWidget(title_label)
        
        # 电池电压数据 - 紧凑网格布局
        battery_group = QGroupBox('电池电压 (1-8)')
        battery_layout = QGridLayout(battery_group)
        battery_layout.setSpacing(int(10 * self.scale_factor))
        battery_layout.setContentsMargins(
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor)
        )
        
        # 数据项样式
        label_font_size = int(17 * self.scale_factor)
        value_font_size = int(18 * self.scale_factor)
        data_label_style = f"QLabel {{ font-weight: 600; font-size: {label_font_size}px; color: #555555; }}"
        data_value_style = f"QLabel {{ font-weight: 700; font-size: {value_font_size}px; padding: {int(6 * self.scale_factor)}px {int(10 * self.scale_factor)}px; background-color: #f8f8f8; border-radius: {int(5 * self.scale_factor)}px; }}"
        
        # 电池1-4
        bat1_label = QLabel('电池1:')
        bat1_label.setStyleSheet(data_label_style)
        battery_layout.addWidget(bat1_label, 0, 0)
        self.battery1_label = QLabel('-- V')
        self.battery1_label.setStyleSheet(data_value_style + f" QLabel {{ color: #0d7c4a; }}")
        battery_layout.addWidget(self.battery1_label, 0, 1)
        
        bat2_label = QLabel('电池2:')
        bat2_label.setStyleSheet(data_label_style)
        battery_layout.addWidget(bat2_label, 0, 2)
        self.battery2_label = QLabel('-- V')
        self.battery2_label.setStyleSheet(data_value_style + f" QLabel {{ color: #0d7c4a; }}")
        battery_layout.addWidget(self.battery2_label, 0, 3)
        
        bat3_label = QLabel('电池3:')
        bat3_label.setStyleSheet(data_label_style)
        battery_layout.addWidget(bat3_label, 1, 0)
        self.battery3_label = QLabel('-- V')
        self.battery3_label.setStyleSheet(data_value_style + f" QLabel {{ color: #0d7c4a; }}")
        battery_layout.addWidget(self.battery3_label, 1, 1)
        
        bat4_label = QLabel('电池4:')
        bat4_label.setStyleSheet(data_label_style)
        battery_layout.addWidget(bat4_label, 1, 2)
        self.battery4_label = QLabel('-- V')
        self.battery4_label.setStyleSheet(data_value_style + f" QLabel {{ color: #0d7c4a; }}")
        battery_layout.addWidget(self.battery4_label, 1, 3)
        
        # 电池5-8
        bat5_label = QLabel('电池5:')
        bat5_label.setStyleSheet(data_label_style)
        battery_layout.addWidget(bat5_label, 2, 0)
        self.battery5_label = QLabel('-- V')
        self.battery5_label.setStyleSheet(data_value_style + f" QLabel {{ color: #0d7c4a; }}")
        battery_layout.addWidget(self.battery5_label, 2, 1)
        
        bat6_label = QLabel('电池6:')
        bat6_label.setStyleSheet(data_label_style)
        battery_layout.addWidget(bat6_label, 2, 2)
        self.battery6_label = QLabel('-- V')
        self.battery6_label.setStyleSheet(data_value_style + f" QLabel {{ color: #0d7c4a; }}")
        battery_layout.addWidget(self.battery6_label, 2, 3)
        
        bat7_label = QLabel('电池7:')
        bat7_label.setStyleSheet(data_label_style)
        battery_layout.addWidget(bat7_label, 3, 0)
        self.battery7_label = QLabel('-- V')
        self.battery7_label.setStyleSheet(data_value_style + f" QLabel {{ color: #0d7c4a; }}")
        battery_layout.addWidget(self.battery7_label, 3, 1)
        
        bat8_label = QLabel('电池8:')
        bat8_label.setStyleSheet(data_label_style)
        battery_layout.addWidget(bat8_label, 3, 2)
        self.battery8_label = QLabel('-- V')
        self.battery8_label.setStyleSheet(data_value_style + f" QLabel {{ color: #0d7c4a; }}")
        battery_layout.addWidget(self.battery8_label, 3, 3)
        
        layout.addWidget(battery_group)
        
        # 系统参数和状态信息 - 水平布局
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setSpacing(int(15 * self.scale_factor))
        
        # 系统参数
        system_group = QGroupBox('系统参数')
        system_layout = QGridLayout(system_group)
        system_layout.setSpacing(int(10 * self.scale_factor))
        system_layout.setContentsMargins(
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor)
        )
        
        total_v_label = QLabel('总电压:')
        total_v_label.setStyleSheet(data_label_style)
        system_layout.addWidget(total_v_label, 0, 0)
        self.total_voltage_label = QLabel('-- V')
        temp_value_font_size = int(20 * self.scale_factor)
        self.total_voltage_label.setStyleSheet(data_value_style + f" QLabel {{ color: #f9ab00; font-size: {temp_value_font_size}px; }}")
        system_layout.addWidget(self.total_voltage_label, 0, 1)
        
        current_label = QLabel('电流:')
        current_label.setStyleSheet(data_label_style)
        system_layout.addWidget(current_label, 1, 0)
        self.current_label = QLabel('-- A')
        self.current_label.setStyleSheet(data_value_style + f" QLabel {{ color: #1a73e8; font-size: {temp_value_font_size}px; }}")
        system_layout.addWidget(self.current_label, 1, 1)
        
        temp1_label = QLabel('温度1:')
        temp1_label.setStyleSheet(data_label_style)
        system_layout.addWidget(temp1_label, 2, 0)
        self.temperature1_label = QLabel('-- ℃')
        self.temperature1_label.setStyleSheet(data_value_style + f" QLabel {{ color: #ea4335; font-size: {temp_value_font_size}px; }}")
        system_layout.addWidget(self.temperature1_label, 2, 1)
        
        temp2_label = QLabel('温度2:')
        temp2_label.setStyleSheet(data_label_style)
        system_layout.addWidget(temp2_label, 3, 0)
        self.temperature2_label = QLabel('-- ℃')
        self.temperature2_label.setStyleSheet(data_value_style + f" QLabel {{ color: #ea4335; font-size: {temp_value_font_size}px; }}")
        system_layout.addWidget(self.temperature2_label, 3, 1)
        
        bottom_layout.addWidget(system_group)
        
        # 状态信息
        status_group = QGroupBox('状态信息')
        status_layout = QGridLayout(status_group)
        status_layout.setSpacing(int(10 * self.scale_factor))
        status_layout.setContentsMargins(
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor),
            int(15 * self.scale_factor)
        )
        
        balance_label = QLabel('平衡状态:')
        balance_label.setStyleSheet(data_label_style)
        status_layout.addWidget(balance_label, 0, 0)
        self.balance_status_label = QLabel('--')
        self.balance_status_label.setStyleSheet(data_value_style + f" QLabel {{ color: #9334e6; font-size: {temp_value_font_size}px; }}")
        status_layout.addWidget(self.balance_status_label, 0, 1)
        
        charge_label = QLabel('充放电状态:')
        charge_label.setStyleSheet(data_label_style)
        status_layout.addWidget(charge_label, 1, 0)
        self.charge_status_label = QLabel('--')
        self.charge_status_label.setStyleSheet(data_value_style + f" QLabel {{ color: #9334e6; font-size: {temp_value_font_size}px; }}")
        status_layout.addWidget(self.charge_status_label, 1, 1)
        
        battery_p_label = QLabel('电量:')
        battery_p_label.setStyleSheet(data_label_style)
        status_layout.addWidget(battery_p_label, 2, 0)
        self.battery_percentage_label = QLabel('-- %')
        self.battery_percentage_label.setStyleSheet(data_value_style + f" QLabel {{ color: #fbbc04; font-size: {temp_value_font_size}px; }}")
        status_layout.addWidget(self.battery_percentage_label, 2, 1)
        
        bottom_layout.addWidget(status_group)
        
        layout.addWidget(bottom_widget)
        
        self.tab_widget.addTab(bms_tab, 'BMS数据')
        
    def create_chart_tab(self):
        chart_tab = QWidget()
        layout = QVBoxLayout(chart_tab)
        
        chart_label = QLabel('数据趋势图 (功能待实现)')
        chart_label.setAlignment(Qt.AlignCenter)
        chart_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #7f8c8d;
                padding: 50px;
            }
        """)
        layout.addWidget(chart_label)
        
        # 图表控制
        chart_control_layout = QHBoxLayout()
        chart_control_layout.addWidget(QLabel('选择数据类型:'))
        
        self.chart_data_type = QComboBox()
        self.chart_data_type.addItems([
            'IN1电流', 'IN1电压', 'IN2电流', 'IN2电压',
            '电池1电压', '电池2电压', '总电压', '电流',
            '温度1', '温度2', '环境温度', '湿度'
        ])
        chart_control_layout.addWidget(self.chart_data_type)
        
        self.clear_chart_button = QPushButton('清除图表')
        chart_control_layout.addWidget(self.clear_chart_button)
        
        layout.addLayout(chart_control_layout)
        
        self.tab_widget.addTab(chart_tab, '数据趋势图')
        
    def create_log_tab(self):
        log_tab = QWidget()
        layout = QVBoxLayout(log_tab)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(QLabel('通信日志:'))
        layout.addWidget(self.log_text)
        
        # 日志控制按钮
        log_control_layout = QHBoxLayout()
        self.clear_log_button = QPushButton('清除日志')
        self.clear_log_button.clicked.connect(self.clear_logs)
        log_control_layout.addWidget(self.clear_log_button)
        
        layout.addLayout(log_control_layout)
        
        self.tab_widget.addTab(log_tab, '通信日志')
        
    def create_recordings_tab(self):
        recordings_tab = QWidget()
        layout = QVBoxLayout(recordings_tab)
        layout.setSpacing(int(8 * self.scale_factor))
        
        # 标题
        title_label = QLabel('数据记录')
        title_font_size = int(18 * self.scale_factor)  # 进一步减小标题字体
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: {title_font_size}px;
                font-weight: 700;
                color: #222222;
                margin-bottom: {int(8 * self.scale_factor)}px;
                font-family: 'Microsoft YaHei';
            }}
        """)
        layout.addWidget(title_label)
        
        # 记录会话标签
        session_label = QLabel('记录会话:')
        session_label.setStyleSheet(f"font-size: {int(13 * self.scale_factor)}px; font-weight: 600; font-family: 'Microsoft YaHei';")  # 进一步减小字体
        layout.addWidget(session_label)
        
        # 全选/取消全选按钮
        select_all_layout = QHBoxLayout()
        self.select_all_button = QPushButton('全选')
        self.select_all_button.setStyleSheet(f"font-size: {int(12 * self.scale_factor)}px; font-family: 'Microsoft YaHei';")
        self.select_all_button.setFixedWidth(int(80 * self.scale_factor))
        self.select_all_button.clicked.connect(self.toggle_select_all)
        select_all_layout.addWidget(self.select_all_button)
        select_all_layout.addStretch()
        layout.addLayout(select_all_layout)
        
        self.recordings_table = QTableWidget(0, 5)
        self.recordings_table.setHorizontalHeaderLabels(['选择', 'ID', '名称', '开始时间', '结束时间'])
        self.recordings_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.recordings_table.setStyleSheet(f"font-size: {int(7 * self.scale_factor)}px; font-family: 'Microsoft YaHei';")  # 进一步减小表格内容字体
        self.recordings_table.horizontalHeader().setStyleSheet(f"font-size: {int(7 * self.scale_factor)}px; font-family: 'Microsoft YaHei'; font-weight: 600;")
        self.recordings_table.verticalHeader().setStyleSheet(f"font-size: {int(7 * self.scale_factor)}px; font-family: 'Microsoft YaHei';")
        self.recordings_table.setMinimumHeight(int(200 * self.scale_factor))  # 设置最小高度
        self.recordings_table.verticalHeader().setDefaultSectionSize(int(20 * self.scale_factor))  # 设置默认行高
        layout.addWidget(self.recordings_table)
        
        # 设置表格列伸缩策略，使其铺满
        self.recordings_table.horizontalHeader().setStretchLastSection(True)            
        self.recordings_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 选择列
        self.recordings_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)  # ID列设置为固定宽度
        self.recordings_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # 名称列
        self.recordings_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # 开始时间列
        self.recordings_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)  # 结束时间列
        
        # 启用行高自适应内容
        self.recordings_table.resizeRowsToContents()

        
        # 记录控制按钮
        record_control_layout = QHBoxLayout()
        record_control_layout.setSpacing(int(6 * self.scale_factor))
        
        self.refresh_recordings_button = QPushButton('刷新记录列表')
        self.refresh_recordings_button.clicked.connect(self.refresh_recordings)
        self.refresh_recordings_button.setStyleSheet(f"font-size: {int(12 * self.scale_factor)}px; font-family: 'Microsoft YaHei'; padding: {int(4 * self.scale_factor)}px;")  # 减小按钮字体并增加内边距
        self.refresh_recordings_button.setFixedWidth(int(110 * self.scale_factor))
        record_control_layout.addWidget(self.refresh_recordings_button)
        
        self.export_record_button = QPushButton('导出选中记录')
        self.export_record_button.clicked.connect(self.export_selected_record)
        self.export_record_button.setStyleSheet(f"font-size: {int(12 * self.scale_factor)}px; font-family: 'Microsoft YaHei'; padding: {int(4 * self.scale_factor)}px;")
        self.export_record_button.setFixedWidth(int(110 * self.scale_factor))
        record_control_layout.addWidget(self.export_record_button)
        
        self.delete_record_button = QPushButton('删除选中记录')
        self.delete_record_button.clicked.connect(self.delete_selected_record)
        self.delete_record_button.setStyleSheet(f"font-size: {int(12 * self.scale_factor)}px; font-family: 'Microsoft YaHei'; padding: {int(4 * self.scale_factor)}px;")
        self.delete_record_button.setFixedWidth(int(110 * self.scale_factor))
        record_control_layout.addWidget(self.delete_record_button)
        
        record_control_layout.addStretch()
        layout.addLayout(record_control_layout)
        
        self.tab_widget.addTab(recordings_tab, '数据记录')
        
    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 连接状态标签
        self.connection_status_label = QLabel('未连接')
        self.connection_status_label.setStyleSheet("QLabel { font-weight: bold; }")
        self.status_bar.addPermanentWidget(self.connection_status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedWidth(150)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # 添加弹簧空间
        self.status_bar.addPermanentWidget(QWidget())
        
        # 自动刷新状态标签
        self.auto_refresh_status_label = QLabel('自动刷新: 已停止')
        self.auto_refresh_status_label.setStyleSheet("QLabel { color: #95a5a6; font-weight: normal; padding: 0 10px; }")
        self.auto_refresh_status_label.setMinimumWidth(120)
        self.status_bar.addPermanentWidget(self.auto_refresh_status_label)
        
        # 记录状态标签
        self.recording_status_label = QLabel('记录: 未记录')
        self.recording_status_label.setStyleSheet("QLabel { color: #95a5a6; font-weight: normal; padding: 0 10px; }")
        self.recording_status_label.setMinimumWidth(120)
        self.status_bar.addPermanentWidget(self.recording_status_label)
        
    def setup_connections(self):
        # 连接信号和槽
        pass
        
    def setup_timers(self):
        self.auto_refresh_timer.timeout.connect(self.refresh_data)
        
    def toggle_connection(self):
        if not self.is_connected:
            self.connect_to_server()
        else:
            self.disconnect_from_server()
            
    def connect_to_server(self):
        ip = self.ip_input.text()
        port = int(self.port_input.text())
        
        if self.modbus_client.connect(ip, port):
            self.is_connected = True
            self.connection_button.setText('断开')
            self.connect_action.setText('断开')
            self.start_record_button.setEnabled(True)
            self.start_record_action.setEnabled(True)
            self.refresh_button.setEnabled(True)
            self.refresh_action.setEnabled(True)
            self.update_connection_status(True)
            self.log_message(f'成功连接到服务器 {ip}:{port}')
        else:
            self.log_message(f'连接服务器失败 {ip}:{port}')
            QMessageBox.critical(self, '连接错误', f'无法连接到服务器 {ip}:{port}')
            
    def disconnect_from_server(self):
        self.modbus_client.disconnect()
        self.is_connected = False
        self.connection_button.setText('连接')
        self.connect_action.setText('连接')
        self.start_record_button.setEnabled(False)
        self.start_record_action.setEnabled(False)
        self.stop_recording()
        self.update_connection_status(False)
        self.log_message('已断开服务器连接')
        
    def update_connection_status(self, connected):
        if connected:
            self.connection_status_label.setText('已连接')
            self.connection_status_label.setStyleSheet("QLabel { color: #27ae60; font-weight: bold; }")
        else:
            self.connection_status_label.setText('未连接')
            self.connection_status_label.setStyleSheet("QLabel { color: #e74c3c; font-weight: bold; }")
            
    def refresh_data(self):
        if not self.is_connected:
            self.log_message('请先连接到服务器')
            return
            
        try:
            # 读取二号板数据
            board_data = self.modbus_client.read_board_data()
            if board_data:
                self.update_board_data_display(board_data)
                self.log_message('二号板数据刷新成功')
            else:
                self.log_message('读取二号板数据失败')
                
            # 读取BMS数据
            bms_data = self.modbus_client.read_bms_data()
            if bms_data:
                self.update_bms_data_display(bms_data)
                self.log_message('BMS数据刷新成功')
            else:
                self.log_message('读取BMS数据失败')
                
            # 如果正在记录，保存数据到数据库
            if self.is_recording and self.recording_id:
                self.db_manager.save_data(self.recording_id, board_data or {}, bms_data or {})
                
        except Exception as e:
            self.log_message(f'刷新数据出错: {str(e)}')
            QMessageBox.critical(self, '数据刷新错误', f'刷新数据时发生错误:\n{str(e)}')
            
    def update_board_data_display(self, data):
        # 更新电源监测数据 (IN1-IN10)
        self.in1_current_label.setText(f"{data.get('IN1_current', '--')} mA")
        self.in1_voltage_label.setText(f"{data.get('IN1_voltage', '--.----')} V")
        self.in2_current_label.setText(f"{data.get('IN2_current', '--')} mA")
        self.in2_voltage_label.setText(f"{data.get('IN2_voltage', '--.----')} V")
        self.in3_current_label.setText(f"{data.get('IN3_current', '--')} mA")
        self.in3_voltage_label.setText(f"{data.get('IN3_voltage', '--.----')} V")
        self.in4_current_label.setText(f"{data.get('IN4_current', '--')} mA")
        self.in4_voltage_label.setText(f"{data.get('IN4_voltage', '--.----')} V")
        self.in5_current_label.setText(f"{data.get('IN5_current', '--')} mA")
        self.in5_voltage_label.setText(f"{data.get('IN5_voltage', '--.----')} V")
        self.in6_current_label.setText(f"{data.get('IN6_current', '--')} mA")
        self.in6_voltage_label.setText(f"{data.get('IN6_voltage', '--.----')} V")
        self.in7_current_label.setText(f"{data.get('IN7_current', '--')} mA")
        self.in7_voltage_label.setText(f"{data.get('IN7_voltage', '--.----')} V")
        self.in8_current_label.setText(f"{data.get('IN8_current', '--')} mA")
        self.in8_voltage_label.setText(f"{data.get('IN8_voltage', '--.----')} V")
        self.in9_current_label.setText(f"{data.get('IN9_current', '--')} mA")
        self.in9_voltage_label.setText(f"{data.get('IN9_voltage', '--.----')} V")
        self.in10_current_label.setText(f"{data.get('IN10_current', '--')} mA")
        self.in10_voltage_label.setText(f"{data.get('IN10_voltage', '--.----')} V")
        self.ac_current_label.setText(f"{data.get('AC_current', '--')} A")
        self.vbat_voltage_label.setText(f"{data.get('VBAT_voltage', '--.----')} V")
        
        # 更新环境监测数据
        temp_value = data.get('temperature_value')
        if temp_value is not None:
            temp_text = f"+{temp_value}" if temp_value >= 0 else f"{temp_value}"
            self.temperature_label.setText(f"{temp_text} ℃")
        else:
            self.temperature_label.setText('-- ℃')
            
        self.humidity_label.setText(f"{data.get('humidity', '--')} %RH")
        
        # 更新安全状态
        door_status = data.get('door_status')
        door_text = '打开' if door_status == 1 else '关闭' if door_status == 0 else '--'
        self.door_status_label.setText(door_text)
        
        water_status = data.get('water_status')
        water_text = '有水' if water_status == 1 else '无水' if water_status == 0 else '--'
        self.water_status_label.setText(water_text)
        
        ac_status = data.get('ac_status')
        ac_text = '备用电源' if ac_status == 1 else '主电源' if ac_status == 0 else '--'
        self.ac_status_label.setText(ac_text)
        
    def update_bms_data_display(self, data):
        # 更新电池电压
        self.battery1_label.setText(f"{data.get('battery1_voltage', '--.---')} V")
        self.battery2_label.setText(f"{data.get('battery2_voltage', '--.---')} V")
        self.battery3_label.setText(f"{data.get('battery3_voltage', '--.---')} V")
        self.battery4_label.setText(f"{data.get('battery4_voltage', '--.---')} V")
        self.battery5_label.setText(f"{data.get('battery5_voltage', '--.---')} V")
        self.battery6_label.setText(f"{data.get('battery6_voltage', '--.---')} V")
        self.battery7_label.setText(f"{data.get('battery7_voltage', '--.---')} V")
        self.battery8_label.setText(f"{data.get('battery8_voltage', '--.---')} V")
        
        # 更新系统参数
        self.total_voltage_label.setText(f"{data.get('total_voltage', '--.---')} V")
        self.current_label.setText(f"{data.get('current', '--.--')} A")
        self.temperature1_label.setText(f"{data.get('temperature1', '--.-')} ℃")
        self.temperature2_label.setText(f"{data.get('temperature2', '--.-')} ℃")
        
        # 更新状态信息
        balance_status = data.get('balance_status')
        balance_text = '正在平衡' if balance_status == 1 else '未平衡' if balance_status == 0 else '--'
        self.balance_status_label.setText(balance_text)
        
        charge_status = data.get('charge_discharge_status')
        charge_map = {1: '充电', 2: '放电', 3: '空闲'}
        charge_text = charge_map.get(charge_status, '--')
        self.charge_status_label.setText(charge_text)
        
        self.battery_percentage_label.setText(f"{data.get('battery_percentage', '--')} %")
        
    def toggle_auto_refresh(self):
        if self.auto_refresh_timer.isActive():
            self.auto_refresh_timer.stop()
            self.auto_refresh_button.setText('开始自动刷新')
            self.update_auto_refresh_status(False)
            self.log_message('已停止自动刷新')
        else:
            interval = self.refresh_interval.value() * 1000  # 转换为毫秒
            self.auto_refresh_timer.start(interval)
            self.auto_refresh_button.setText('停止自动刷新')
            self.update_auto_refresh_status(True)
            self.log_message(f'已开始自动刷新，间隔 {self.refresh_interval.value()} 秒')
            
    def start_recording(self):
        if not self.is_connected:
            self.log_message('请先连接到服务器')
            return
            
        try:
            recording_name = self.record_name_input.text() or f'记录_{ QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss") }'
            
            # 这里应该调用数据库管理器开始记录
            self.recording_id = self.db_manager.start_recording(recording_name)
            self.is_recording = True
            
            self.start_record_button.setEnabled(False)
            self.start_record_action.setEnabled(False)
            self.stop_record_button.setEnabled(True)
            self.stop_record_action.setEnabled(True)
            
            self.record_status_label.setText(f'状态: 记录中 - {recording_name}')
            self.update_recording_status(True, recording_name)
            self.log_message(f'开始数据记录: {recording_name}')
        except Exception as e:
            self.log_message(f'开始记录出错: {str(e)}')
            QMessageBox.critical(self, '记录错误', f'开始记录时发生错误:\n{str(e)}')
            
    def stop_recording(self):
        try:
            if self.is_recording:
                # 这里应该调用数据库管理器停止记录
                self.db_manager.stop_recording(self.recording_id)
                self.is_recording = False
                self.recording_id = None
                
                self.start_record_button.setEnabled(True)
                self.start_record_action.setEnabled(True)
                self.stop_record_button.setEnabled(False)
                self.stop_record_action.setEnabled(False)
                
                self.record_status_label.setText('状态: 未记录')
                self.update_recording_status(False)
                self.log_message('数据记录已停止')
        except Exception as e:
            self.log_message(f'停止记录出错: {str(e)}')
            QMessageBox.critical(self, '记录错误', f'停止记录时发生错误:\n{str(e)}')
            
    def connect_scanner_signals(self):
        """连接扫描器信号"""
        self.scanner.device_found.connect(self.on_device_found)
        self.scanner.scan_progress.connect(self.on_scan_progress)
        self.scanner.scan_finished.connect(self.on_scan_finished)
        self.scanner.scan_error.connect(self.on_scan_error)
        self.scanner.log_message.connect(self.on_scan_log_message)
        
    def on_device_found(self, ip, port):
        """处理发现设备信号"""
        device_key = f"{ip}:{port}"
        # 检查是否已经添加过该设备到表格中
        if device_key not in self.found_devices_set:
            self.found_devices_set.add(device_key)
            self.add_scan_result(ip, port)
        
    def on_scan_progress(self, current, total):
        """处理扫描进度信号"""
        # 可以在这里更新进度条
        pass
        
    def on_scan_finished(self, devices):
        """处理扫描完成信号"""
        self.progress_bar.setVisible(False)
        self.scan_button.setEnabled(True)
        self.stop_scan_button.setEnabled(False)
        self.log_message(f'设备扫描完成，共发现 {len(devices)} 个设备')
        
    def on_scan_error(self, error_msg):
        """处理扫描错误信号"""
        self.progress_bar.setVisible(False)
        self.scan_button.setEnabled(True)
        self.stop_scan_button.setEnabled(False)
        self.log_message(f'设备扫描出错: {error_msg}')
        QMessageBox.critical(self, '扫描错误', f'扫描设备时发生错误:\n{error_msg}')
        
    def on_scan_log_message(self, message):
        """处理扫描日志消息信号"""
        self.log_message(message)
        
    def scan_devices(self):
        """扫描网络中的Modbus设备"""
        self.log_message('开始扫描网络中的Modbus设备...')
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 持续滚动
        
        try:
            # 获取IP范围
            base_ip = self.ip_input.text()
            # 提取基础IP地址段
            ip_parts = base_ip.split('.')
            if len(ip_parts) != 4:
                self.log_message('无效的IP地址格式')
                self.progress_bar.setVisible(False)
                return
            
            # 使用新的扫描模块进行扫描
            if self.scan_thread and self.scan_thread.isRunning():
                self.log_message('扫描已在进行中...')
                return
                
            self.scan_button.setEnabled(False)
            self.stop_scan_button.setEnabled(True)
            
            # 清空现有扫描结果和设备集合
            self.scan_results.setRowCount(0)
            self.found_devices_set.clear()
            
            # 使用50个并发线程进行扫描
            self.scan_thread = ScannerThread(self.scanner, base_ip, 502, 0.3, (1, 50), 50)
            self.scan_thread.start()
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.scan_button.setEnabled(True)
            self.stop_scan_button.setEnabled(False)
            self.log_message(f'设备扫描出错: {str(e)}')
            QMessageBox.critical(self, '扫描错误', f'扫描设备时发生错误:\n{str(e)}')
            
    def stop_scan(self):
        """停止扫描"""
        if self.scan_thread and self.scan_thread.isRunning():
            self.scanner.stop_scan()
            self.log_message('正在停止扫描...')

        
        select_button = QPushButton('选择')
        select_button.clicked.connect(lambda: self.select_device(ip, port))
        self.scan_results.setCellWidget(row, 2, select_button)
        
    def select_device(self, ip, port):
        self.ip_input.setText(ip)
        self.port_input.setText(str(port))
        self.log_message(f'已选择设备: {ip}:{port}')
        
    def refresh_recordings(self):
        """刷新记录列表"""
        try:
            # 从数据库获取记录会话列表
            recordings = self.db_manager.get_recordings()
            
            # 清空现有记录
            self.recordings_table.setRowCount(0)
            
            # 填充记录数据
            for recording in recordings:
                row = self.recordings_table.rowCount()
                self.recordings_table.insertRow(row)
                
                # 添加记录数据并设置字体和颜色
                recording_id, name, start_time, end_time = recording
                
                # 选择列 - 添加复选框
                checkbox = QTableWidgetItem()
                checkbox.setCheckState(Qt.Unchecked)
                self.recordings_table.setItem(row, 0, checkbox)
                
                # ID列
                id_item = QTableWidgetItem(str(recording_id))
                id_item.setFont(QFont("Microsoft YaHei", int(7 * self.scale_factor)))
                id_item.setForeground(QColor("#222222"))
                self.recordings_table.setItem(row, 1, id_item)
                
                # 名称列
                name_item = QTableWidgetItem(name)
                name_item.setFont(QFont("Microsoft YaHei", int(7 * self.scale_factor)))
                name_item.setForeground(QColor("#222222"))
                self.recordings_table.setItem(row, 2, name_item)
                
                # 开始时间列
                start_item = QTableWidgetItem(start_time)
                start_item.setFont(QFont("Microsoft YaHei", int(7 * self.scale_factor)))
                start_item.setForeground(QColor("#222222"))
                self.recordings_table.setItem(row, 3, start_item)
                
                # 结束时间列
                end_item = QTableWidgetItem(end_time or '')
                end_item.setFont(QFont("Microsoft YaHei", int(7 * self.scale_factor)))
                end_item.setForeground(QColor("#222222"))
                self.recordings_table.setItem(row, 4, end_item)
                
            # 调整行高以适应内容
            for row in range(self.recordings_table.rowCount()):
                self.recordings_table.setRowHeight(row, int(18 * self.scale_factor))
                
            # 确保ID列宽度适合内容
            self.recordings_table.resizeColumnToContents(1)
            
            self.log_message(f'记录列表已刷新，共 {len(recordings)} 条记录')
        except Exception as e:
            self.log_message(f'刷新记录列表出错: {str(e)}')
            QMessageBox.critical(self, '错误', f'刷新记录列表时发生错误:\n{str(e)}')
            
    def delete_selected_record(self):
        """删除选中的记录"""
        try:
            # 获取选中复选框的行
            selected_rows = []
            for row in range(self.recordings_table.rowCount()):
                checkbox_item = self.recordings_table.item(row, 0)
                if checkbox_item and checkbox_item.checkState() == Qt.Checked:
                    selected_rows.append(row)
            
            if not selected_rows:
                QMessageBox.warning(self, '警告', '请先选择要删除的记录')
                return
                
            # 确认删除
            reply = QMessageBox.question(self, '确认删除', '确定要删除选中的记录吗？此操作不可恢复。',
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # 删除选中的记录
                for row in selected_rows:
                    recording_id = self.recordings_table.item(row, 1).text()
                    self.db_manager.delete_recording(recording_id)
                    
                # 刷新记录列表
                self.refresh_recordings()
                self.log_message(f'已删除 {len(selected_rows)} 条记录')
                
        except Exception as e:
            self.log_message(f'删除记录出错: {str(e)}')

            QMessageBox.critical(self, '错误', f'删除记录时发生错误:\n{str(e)}')
            
    def toggle_select_all(self):
        """全选/取消全选功能"""
        # 检查当前是否全部选中
        all_selected = True
        for row in range(self.recordings_table.rowCount()):
            checkbox_item = self.recordings_table.item(row, 0)
            if not checkbox_item or checkbox_item.checkState() != Qt.Checked:
                all_selected = False
                break
                
        # 设置所有复选框的状态
        new_state = Qt.Unchecked if all_selected else Qt.Checked
        for row in range(self.recordings_table.rowCount()):
            checkbox_item = self.recordings_table.item(row, 0)
            if checkbox_item:
                checkbox_item.setCheckState(new_state)
                
        # 更新按钮文本
        self.select_all_button.setText('取消全选' if new_state == Qt.Checked else '全选')
        
    def export_selected_record(self):
        """导出选中的记录为Excel文件"""
        try:
            # 获取选中复选框的行
            selected_rows = []
            for row in range(self.recordings_table.rowCount()):
                checkbox_item = self.recordings_table.item(row, 0)
                if checkbox_item and checkbox_item.checkState() == Qt.Checked:
                    selected_rows.append(row)
            
            if not selected_rows:
                QMessageBox.warning(self, '警告', '请先选择要导出的记录')
                return
                
            # 如果只选择了一个记录，使用保存文件对话框
            if len(selected_rows) == 1:
                # 选择保存路径
                file_path, _ = QFileDialog.getSaveFileName(
                    self, 
                    '导出记录为Excel文件', 
                    '', 
                    'Excel文件 (*.xlsx);;所有文件 (*)'
                )
                
                if not file_path:
                    return
                    
                # 如果用户没有添加扩展名，自动添加.xlsx
                if not file_path.endswith('.xlsx'):
                    file_path += '.xlsx'
                    
                # 导出选中的记录
                row = selected_rows[0]
                recording_id = self.recordings_table.item(row, 1).text()
                
                # 导出记录
                if self.db_manager.export_recording_to_excel(recording_id, file_path):
                    self.log_message(f'成功导出记录 {recording_id} 到 {file_path}')
                    QMessageBox.information(self, '导出成功', f'成功导出记录 {recording_id}')
                else:
                    self.log_message('导出记录失败')
                    QMessageBox.critical(self, '导出失败', '导出记录时发生错误')
            else:
                # 如果选择了多个记录，使用选择文件夹对话框
                directory = QFileDialog.getExistingDirectory(
                    self, 
                    '选择导出目录', 
                    ''
                )
                
                if not directory:
                    return
                    
                # 导出选中的记录
                success_count = 0
                failed_records = []
                
                for row in selected_rows:
                    recording_id = self.recordings_table.item(row, 1).text()
                    
                    # 为每个记录创建独立的文件名
                    record_file_path = os.path.join(directory, f"记录{recording_id}.xlsx")
                    
                    # 导出记录
                    if self.db_manager.export_recording_to_excel(recording_id, record_file_path):
                        success_count += 1
                    else:
                        failed_records.append(recording_id)
                        
                if success_count > 0:
                    message = f'成功导出 {success_count} 条记录到 {directory}'
                    if failed_records:
                        message += f'\n以下记录导出失败: {", ".join(failed_records)}'
                    self.log_message(message)
                    QMessageBox.information(self, '导出成功', message)
                else:
                    self.log_message('导出记录失败')
                    QMessageBox.critical(self, '导出失败', '导出记录时发生错误')
                
        except Exception as e:
            self.log_message(f'导出记录出错: {str(e)}')
            QMessageBox.critical(self, '错误', f'导出记录时发生错误:\n{str(e)}')
    def clear_logs(self):
        self.log_text.clear()
        self.log_message('日志已清除')
        
    def log_message(self, message):
        timestamp = QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss')
        log_entry = f'[{timestamp}] {message}'
        self.log_text.append(log_entry)
        
        # 限制日志行数
        max_lines = 1000
        lines = self.log_text.toPlainText().split('\n')
        if len(lines) > max_lines:
            self.log_text.setPlainText('\n'.join(lines[-max_lines:]))