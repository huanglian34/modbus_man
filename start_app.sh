#!/bin/bash

# Modbus数据监控面板启动脚本
# 作者: Qoder AI Assistant
# 日期: $(date)

echo "================================"
echo "Modbus数据监控面板启动脚本"
echo "================================"
echo

# 检查是否在正确的目录
if [ ! -f "app.py" ]; then
    echo "错误: 未找到 app.py 文件"
    echo "请确保此脚本位于项目根目录下"
    echo
    read -p "按回车键继续..."
    exit 1
fi

# 检查Python是否已安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未检测到Python3"
    echo "请先安装Python 3.6或更高版本"
    echo
    read -p "按回车键继续..."
    exit 1
fi

echo "检查依赖包..."
echo

# 检查并安装依赖
if [ ! -f "requirements.txt" ]; then
    echo "警告: 未找到 requirements.txt 文件"
    echo "跳过依赖检查..."
    echo
else
    echo "安装依赖包..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "警告: 依赖包安装失败，继续启动应用..."
        echo
    else
        echo "依赖包安装完成"
        echo
    fi
fi

echo "启动Modbus数据监控面板..."
echo
echo "应用将在默认浏览器中打开"
echo "访问地址: http://127.0.0.1:5000"
echo
echo "按 Ctrl+C 可以停止应用"
echo

# 启动应用并打开浏览器 (根据操作系统)
case "$(uname -s)" in
    Darwin*)
        # macOS
        open http://127.0.0.1:5000
        ;;
    Linux*)
        # Linux
        if command -v xdg-open &> /dev/null; then
            xdg-open http://127.0.0.1:5000
        elif command -v gnome-open &> /dev/null; then
            gnome-open http://127.0.0.1:5000
        elif command -v kde-open &> /dev/null; then
            kde-open http://127.0.0.1:5000
        else
            echo "无法自动打开浏览器，请手动访问 http://127.0.0.1:5000"
        fi
        ;;
    *)
        echo "无法自动打开浏览器，请手动访问 http://127.0.0.1:5000"
        ;;
esac

python3 app.py