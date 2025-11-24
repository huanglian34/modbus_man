# Modbus数据监控面板

一个基于Python Flask和pymodbus的Web应用程序，用于通过Modbus TCP协议从服务器读取数据并在网页上实时显示。

## 功能特性

1. 通过Modbus TCP协议从服务器读取数据并在网页上实时显示
2. 支持配置服务器IP地址和端口号
3. 实时显示二号板和BMS保护板的各项监测数据
4. 记录并显示所有发送和接收的Modbus通信日志
5. 提供手动刷新和自动轮询功能
6. 响应式布局设计，支持各种设备屏幕
7. 连接状态实时监测和断线自动检测
8. 通信日志清除功能

## 技术栈

- 后端: Python + Flask + pymodbus
- 前端: HTML5 + CSS3 + JavaScript
- 通信协议: Modbus TCP

## 安装与运行

### 方法一：使用一键运行脚本（推荐）

#### Windows系统：
双击运行 `start_app.bat` 脚本启动应用
双击运行 `stop_app.bat` 脚本停止应用

#### Linux/macOS系统：
```bash
chmod +x start_app.sh
./start_app.sh
```
要停止应用，请使用 Ctrl+C 或关闭终端窗口

### 方法二：手动运行

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 运行应用:
```bash
python app.py
```

3. 访问应用:
打开浏览器访问 `http://localhost:5000`

## 使用说明

1. 在连接配置面板中输入Modbus服务器的IP地址和端口号
2. 点击"连接"按钮建立连接
3. 连接成功后，可以点击"手动刷新"获取数据，或点击"开始自动刷新"启用自动轮询
4. 在"通信日志"面板中查看所有的通信记录
5. 可以点击"清除日志"按钮清除通信日志

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
├── app.py              # Flask应用主文件
├── requirements.txt    # 依赖包列表
├── README.md           # 说明文档
├── start_app.bat       # Windows一键启动脚本
├── stop_app.bat        # Windows一键停止脚本
├── start_app.sh        # Linux/macOS一键启动脚本
├── templates/
│   └── index.html      # 主页面模板
└── static/
    ├── css/
    │   ├── style.css   # 主样式文件
    │   └── message.css # 消息提示样式
    └── js/
        └── script.js   # JavaScript逻辑
```