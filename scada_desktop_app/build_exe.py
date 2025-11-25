#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌面应用程序打包脚本
使用PyInstaller将Python应用程序打包成独立的exe文件
"""

import os
import sys
from PyInstaller.__main__ import run

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 设置工作目录为当前目录（scada_desktop_app）
os.chdir(current_dir)

# PyInstaller打包参数
opts = [
    # 主程序入口文件
    'main.py',
    
    # 生成单个exe文件
    '--onefile',
    
    # 窗口模式（无控制台窗口）
    '--windowed',
    
    # 指定应用程序名称
    '--name=斯络通上位机监控系统',
    
    # 指定图标（如果有的话）
    # '--icon=icon.ico',
    
    # 包含额外的文件和目录
    '--add-data=ui;ui',
    '--add-data=utils;utils',
    
    # 隐藏导入的模块（确保这些模块被包含）
    '--hidden-import=PyQt5.sip',
    '--hidden-import=PyQt5.QtCore',
    '--hidden-import=PyQt5.QtGui',
    '--hidden-import=PyQt5.QtWidgets',
    '--hidden-import=pandas',
    '--hidden-import=numpy',
    '--hidden-import=openpyxl',
    '--hidden-import=pymodbus',
    '--hidden-import=pymodbus.client',
    '--hidden-import=pymodbus.client.tcp',
    '--hidden-import=asyncio',  # pymodbus需要asyncio
    
    # 不排除必要的模块
    # '--exclude-module=matplotlib',
    # '--exclude-module=scipy',
    # '--exclude-module=PIL',
    # '--exclude-module=tkinter',
    # '--exclude-module=unittest',
    # '--exclude-module=pydoc',
    # '--exclude-module=asyncio',
    
    # 指定输出目录
    '--distpath=dist',
    
    # 指定构建目录
    '--workpath=build',
    
    # 指定spec文件目录
    '--specpath=.',
    
    # 清理之前的构建
    '--clean',
    
    # 详细输出
    '--log-level=INFO'
]

if __name__ == '__main__':
    print("开始打包斯络通上位机监控系统...")
    print(f"工作目录: {os.getcwd()}")
    
    try:
        # 执行PyInstaller打包
        run(opts)
        print("打包完成！生成的exe文件位于 dist/ 目录中")
        print("生成的文件名: 斯络通上位机监控系统.exe")
        
        # 显示生成文件的大小
        exe_path = os.path.join('dist', '斯络通上位机监控系统.exe')
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path)
            print(f"生成的exe文件大小: {size / (1024*1024):.1f} MB")
    except Exception as e:
        print(f"打包过程中出现错误: {e}")
        sys.exit(1)