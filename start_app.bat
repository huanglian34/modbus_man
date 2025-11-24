@echo off
chcp 65001 >nul
REM Modbus数据监控面板启动脚本
REM 作者: Qoder AI Assistant
REM 日期: %date%

title Modbus数据监控面板

echo ================================
echo Modbus数据监控面板启动脚本
echo ================================
echo.

REM 检查是否在正确的目录
if not exist "app.py" (
    echo 错误: 未找到 app.py 文件
    echo 请确保此脚本位于项目根目录下
    echo.
    pause
    exit /b 1
)


@REM REM 检查Python是否已安装
@REM python --version >nul 2>&1
@REM if %errorlevel% neq 0 (
@REM     echo 错误: 未检测到Python
@REM     echo 请先安装Python 3.6或更高版本
@REM     echo.
@REM     pause
@REM     exit /b 1
@REM )

@REM echo 检查依赖包...
@REM echo.

@REM REM 检查并安装依赖
@REM if not exist "requirements.txt" (
@REM     echo 警告: 未找到 requirements.txt 文件
@REM     echo 跳过依赖检查...
@REM     echo.
@REM ) else (
@REM     echo 安装依赖包...
@REM     pip install -r requirements.txt
@REM     if %errorlevel% neq 0 (
@REM         echo 警告: 依赖包安装失败，继续启动应用...
@REM         echo.
@REM     ) else (
@REM         echo 依赖包安装完成
@REM         echo.
@REM     )
@REM )


echo 启动Modbus数据监控面板...
echo.
echo 应用将在默认浏览器中打开
echo 访问地址: http://127.0.0.1:5000
echo.
echo 按 Ctrl+C 可以停止应用
echo.

REM 设置环境变量以确保UTF-8编码
set PYTHONIOENCODING=utf-8

REM 启动应用并打开浏览器
start "" http://127.0.0.1:5000
python app.py

pause