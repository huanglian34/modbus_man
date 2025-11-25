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
project_root = os.path.dirname(current_dir)

# 设置工作目录为项目根目录
os.chdir(project_root)

# PyInstaller打包参数
opts = [
    # 主程序入口文件
    'scada_desktop_app/main.py',
    
    # 生成单个exe文件
    '--onefile',
    
    # 窗口模式（无控制台窗口）
    '--windowed',
    
    # 指定图标（如果有的话）
    # '--icon=icon.ico',
    
    # 包含额外的文件和目录
    '--add-data=scada_desktop_app/ui;ui',
    '--add-data=scada_desktop_app/utils;utils',
    '--add-data=scada_desktop_app/models;models',
    
    # 隐藏导入的模块
    '--hidden-import=PyQt5.sip',
    '--hidden-import=PyQt5.QtCore',
    '--hidden-import=PyQt5.QtGui',
    '--hidden-import=PyQt5.QtWidgets',
    
    # 排除不必要的模块以减小文件大小
    '--exclude-module=matplotlib',
    '--exclude-module=numpy',
    '--exclude-module=scipy',
    '--exclude-module=PIL',
    
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
    print("开始打包SCADA桌面应用程序...")
    print(f"工作目录: {os.getcwd()}")
    
    try:
        # 执行PyInstaller打包
        run(opts)
        print("打包完成！生成的exe文件位于 dist/ 目录中")
    except Exception as e:
        print(f"打包过程中出现错误: {e}")
        sys.exit(1)