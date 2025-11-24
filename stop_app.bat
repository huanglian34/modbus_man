@echo off
chcp 65001 >nul
REM Modbus数据监控面板停止脚本
REM 作者: Qoder AI Assistant
REM 日期: %date%

title 停止Modbus应用

echo ================================
echo Modbus数据监控面板停止脚本
echo ================================
echo.

echo 正在停止所有Python进程...
echo.

taskkill /f /im python.exe

echo.
echo 所有Python进程已停止
echo.

pause