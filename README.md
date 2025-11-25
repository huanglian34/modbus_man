# SCADA上位机监控系统

一个基于Python PyQt5的桌面应用程序，用于通过Modbus TCP协议从服务器读取数据并在图形界面中实时显示。

## 功能特性

1. 通过Modbus TCP协议从服务器读取数据并在图形界面中实时显示
2. 支持配置服务器IP地址和端口号
3. 实时显示二号板和BMS保护板的各项监测数据
4. 记录并显示所有发送和接收的Modbus通信日志
5. 提供手动刷新和自动轮询功能
6. 数据记录功能，可将监测数据保存到本地数据库
7. 数据导出功能，支持将记录数据导出为Excel文件
8. 网络设备扫描功能，自动发现Modbus设备
9. 响应式布局设计，支持各种屏幕分辨率
10. 连接状态实时监测和断线自动检测
11. 通信日志清除功能

## 技术栈

- 后端: Python + PyQt5 + sqlite3 + pymodbus
- 前端: PyQt5 GUI框架
- 通信协议: Modbus TCP
- 数据存储: SQLite数据库
- 数据导出: pandas + openpyxl (Excel文件)

## 安装与运行

### 方法一：使用打包的exe文件（推荐）

直接运行 `scada_desktop_app/dist/SCADA上位机监控系统.exe` 文件启动应用

### 方法二：从源码运行

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 运行应用:
```bash
cd scada_desktop_app
python main.py
```

### 方法三：重新打包exe文件

1. 安装打包工具:
```bash
pip install pyinstaller
```

2. 打包应用:
```bash
cd scada_desktop_app
pyinstaller --noconfirm --onefile --windowed main.py
```

打包后的exe文件将位于 `scada_desktop_app/dist/` 目录中

## 使用说明

1. 在连接配置面板中输入Modbus服务器的IP地址和端口号
2. 点击"连接"按钮建立连接
3. 连接成功后，可以点击"手动刷新"获取数据，或点击"开始自动刷新"启用自动轮询
4. 在"通信日志"面板中查看所有的通信记录
5. 可以点击"清除日志"按钮清除通信日志
6. 使用"扫描设备"功能自动发现网络中的Modbus设备
7. 在"数据记录"面板中查看、导出或删除历史记录
8. 点击"开始记录数据"按钮开始记录监测数据

## 数据说明

### 二号板数据
- 电源监测: IN1-IN10通道的电流和电压值
- 环境监测: 温度和湿度值
- 安全状态: 门状态、水浸状态、AC检测状态

### BMS保护板数据
- 电池电压: 8节电池的单体电压和总电压
- 系统参数: 电流、温度传感器读数
- 状态信息: 平衡状态、充放电状态、电量百分比

## 项目结构

```
modbus_man/
├── scada_desktop_app/
│   ├── main.py              # 应用程序入口文件
│   ├── requirements.txt     # 依赖包列表
│   ├── README.md            # 说明文档
│   ├── ui/
│   │   └── main_window.py   # 主窗口界面文件
│   ├── utils/
│   │   ├── modbus_client.py # Modbus客户端模块
│   │   ├── database.py      # 数据库管理模块
│   │   ├── scanner.py       # 网络扫描模块
│   │   └── test_scanner.py  # 扫描模块测试文件
│   └── dist/
│       └── SCADA上位机监控系统.exe  # 打包后的可执行文件
├── app.py                   # Flask Web应用主文件（旧版本）
├── requirements.txt         # Web应用依赖包列表（旧版本）
├── README.md                # 本说明文档
├── start_app.bat            # Windows一键启动脚本（旧版本）
├── stop_app.bat             # Windows一键停止脚本（旧版本）
├── start_app.sh             # Linux/macOS一键启动脚本（旧版本）
├── templates/
│   └── index.html           # Web应用主页面模板（旧版本）
└── static/
    ├── css/
    │   ├── style.css        # Web应用主样式文件（旧版本）
    │   └── message.css      # Web应用消息提示样式（旧版本）
    └── js/
        └── script.js        # Web应用JavaScript逻辑（旧版本）
```

## 系统要求

- Windows 7/8/10/11 或更高版本
- Python 3.7 或更高版本（从源码运行时）
- 至少4GB内存
- 100MB可用磁盘空间

## 常见问题

### 1. 连接失败
- 检查IP地址和端口号是否正确
- 确保Modbus服务器正在运行且网络连通
- 检查防火墙设置是否阻止了连接

### 2. 数据显示异常
- 检查Modbus寄存器地址配置是否正确
- 确认设备固件版本与应用程序兼容

### 3. 扫描功能无结果
- 确保网络连通性良好
- 检查目标设备是否支持Modbus TCP协议
- 调整扫描超时时间参数

## 更新日志

### v1.0.0
- 初始版本发布
- 实现基本的Modbus数据读取和显示功能
- 添加数据记录和导出功能
- 实现网络设备扫描功能
- 添加自动刷新和手动刷新功能

## 许可证

本项目仅供学习和参考使用。