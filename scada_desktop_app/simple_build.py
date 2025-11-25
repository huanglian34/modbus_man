#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化打包脚本
专注于确保基本功能正常工作
"""

import os
import sys
from PyInstaller.__main__ import run

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 设置工作目录为当前目录（scada_desktop_app）
os.chdir(current_dir)

# 简化的PyInstaller打包参数
opts = [
    # 主程序入口文件
    'main.py',
    
    # 生成单个exe文件
    '--onefile',
    
    # 窗口模式（无控制台窗口）
    '--windowed',
    
    # 指定应用程序名称
    '--name=斯络通上位机监控系统',
    
    # 包含额外的文件和目录
    '--add-data=ui;ui',
    '--add-data=utils;utils',
    
    # 指定输出目录
    '--distpath=dist',
    
    # 清理之前的构建
    '--clean',
    
    # 减少日志输出
    '--log-level=WARN'
]

if __name__ == '__main__':
    print("开始简化打包斯络通上位机监控系统...")
    print(f"工作目录: {os.getcwd()}")
    
    try:
        # 执行PyInstaller打包
        run(opts)
        print("简化打包完成！")
        
        # 显示生成文件的大小
        exe_path = os.path.join('dist', '斯络通上位机监控系统.exe')
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path)
            print(f"生成的exe文件大小: {size / (1024*1024):.1f} MB")
    except Exception as e:
        print(f"打包过程中出现错误: {e}")
        sys.exit(1)