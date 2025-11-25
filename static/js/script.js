// DOM元素引用
const elements = {
    // 连接配置
    serverIp: document.getElementById('serverIp'),
    serverPort: document.getElementById('serverPort'),
    connectBtn: document.getElementById('connectBtn'),
    disconnectBtn: document.getElementById('disconnectBtn'),
    
    // 控制面板
    refreshBtn: document.getElementById('refreshBtn'),
    autoRefreshBtn: document.getElementById('autoRefreshBtn'),
    refreshInterval: document.getElementById('refreshInterval'),
    
    // 数据记录控制
    recordingName: document.getElementById('recordingName'),
    startRecordingBtn: document.getElementById('startRecordingBtn'),
    stopRecordingBtn: document.getElementById('stopRecordingBtn'),
    managementBtn: document.getElementById('managementBtn'),
    
    // 连接状态
    connectionStatus: document.getElementById('connectionStatus'),
    statusIndicator: document.getElementById('statusIndicator'),
    statusText: document.getElementById('statusText'),
    
    // 二号板数据元素
    in1Current: document.getElementById('in1Current'),
    in1Voltage: document.getElementById('in1Voltage'),
    in2Current: document.getElementById('in2Current'),
    in2Voltage: document.getElementById('in2Voltage'),
    in3Current: document.getElementById('in3Current'),
    in3Voltage: document.getElementById('in3Voltage'),
    in4Current: document.getElementById('in4Current'),
    in4Voltage: document.getElementById('in4Voltage'),
    in5Current: document.getElementById('in5Current'),
    in5Voltage: document.getElementById('in5Voltage'),
    in6Current: document.getElementById('in6Current'),
    in6Voltage: document.getElementById('in6Voltage'),
    in7Current: document.getElementById('in7Current'),
    in7Voltage: document.getElementById('in7Voltage'),
    in8Current: document.getElementById('in8Current'),
    in8Voltage: document.getElementById('in8Voltage'),
    in9Current: document.getElementById('in9Current'),
    in9Voltage: document.getElementById('in9Voltage'),
    in10Current: document.getElementById('in10Current'),
    in10Voltage: document.getElementById('in10Voltage'),
    acCurrent: document.getElementById('acCurrent'),
    vbatVoltage: document.getElementById('vbatVoltage'),
    temperature: document.getElementById('temperature'),
    humidity: document.getElementById('humidity'),
    doorStatus: document.getElementById('doorStatus'),
    waterStatus: document.getElementById('waterStatus'),
    acStatus: document.getElementById('acStatus'),
    
    // BMS数据元素
    battery1Voltage: document.getElementById('battery1Voltage'),
    battery2Voltage: document.getElementById('battery2Voltage'),
    battery3Voltage: document.getElementById('battery3Voltage'),
    battery4Voltage: document.getElementById('battery4Voltage'),
    battery5Voltage: document.getElementById('battery5Voltage'),
    battery6Voltage: document.getElementById('battery6Voltage'),
    battery7Voltage: document.getElementById('battery7Voltage'),
    battery8Voltage: document.getElementById('battery8Voltage'),
    totalVoltage: document.getElementById('totalVoltage'),
    current: document.getElementById('current'),
    temperature1: document.getElementById('temperature1'),
    temperature2: document.getElementById('temperature2'),
    balanceStatus: document.getElementById('balanceStatus'),
    chargeDischargeStatus: document.getElementById('chargeDischargeStatus'),
    batteryPercentage: document.getElementById('batteryPercentage'),
    
    // 概览数据元素
    summaryIn1Voltage: document.getElementById('summaryIn1Voltage'),
    summaryIn4Voltage: document.getElementById('summaryIn4Voltage'),
    summaryIn7Voltage: document.getElementById('summaryIn7Voltage'),
    summaryIn10Voltage: document.getElementById('summaryIn10Voltage'),
    summaryBattery1Voltage: document.getElementById('summaryBattery1Voltage'),
    summaryBattery4Voltage: document.getElementById('summaryBattery4Voltage'),
    summaryTotalVoltage: document.getElementById('summaryTotalVoltage'),
    summaryCurrent: document.getElementById('summaryCurrent'),
    summaryBatteryPercentage: document.getElementById('summaryBatteryPercentage'),
    
    // 日志
    logContent: document.getElementById('logContent'),
    
    // 图表相关元素
    chartDataType: document.getElementById('chartDataType'),
    clearChartBtn: document.getElementById('clearChartBtn'),
    
    // 新增元素
    beijingTime: document.getElementById('beijingTime'),
    welcomeText: document.getElementById('welcomeText'),
    
    // 扫描设备相关元素
    scanDevicesBtn: document.getElementById('scanDevicesBtn'),
    stopScanBtn: document.getElementById('stopScanBtn'),
    scanResultsContainer: document.getElementById('scanResultsContainer'),
    scanProgress: document.getElementById('scanProgress'),
    scanProgressText: document.getElementById('scanProgressText'),
    scanResultsList: document.getElementById('scanResultsList'),
    
    // 悬浮刷新按钮
    floatingRefreshBtn: document.getElementById('floatingRefreshBtn')
};

// 全局变量
let isConnected = false;
let autoRefreshInterval = null;
let connectionCheckInterval = null;
let isRecording = false;
let recordingId = null;

// 图表相关变量
let dataChart = null;
let chartData = {};

// 初始化应用
function initApp() {
    loadConfig();
    setupEventListeners();
    updateWelcomeMessage();
    startBeijingTime();
    startConnectionCheck();
    startLogUpdate();
    initChart();
}

// 加载配置
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        elements.serverIp.value = config.host;
        elements.serverPort.value = config.port;
    } catch (error) {
        console.error('加载配置失败:', error);
    }
}

// 设置事件监听器
function setupEventListeners() {
    elements.connectBtn.addEventListener('click', connect);
    elements.disconnectBtn.addEventListener('click', disconnect);
    elements.refreshBtn.addEventListener('click', refreshData);
    elements.autoRefreshBtn.addEventListener('click', toggleAutoRefresh);
    elements.chartDataType.addEventListener('change', updateChart);
    elements.clearChartBtn.addEventListener('click', clearChart);
    
    // 数据记录控制事件
    elements.startRecordingBtn.addEventListener('click', startRecording);
    elements.stopRecordingBtn.addEventListener('click', stopRecording);
    elements.managementBtn.addEventListener('click', () => {
        window.location.href = '/management';
    });
    
    // 扫描设备事件
    elements.scanDevicesBtn.addEventListener('click', scanDevices);
    elements.stopScanBtn.addEventListener('click', stopScanDevices);
    
    // 监听刷新间隔输入框的变化
    elements.refreshInterval.addEventListener('change', updateAutoRefreshInterval);
    elements.refreshInterval.addEventListener('input', updateAutoRefreshInterval);
    
    // 悬浮刷新按钮事件
    if (elements.floatingRefreshBtn) {
        elements.floatingRefreshBtn.addEventListener('click', refreshData);
    }
}

// 更新自动刷新间隔
function updateAutoRefreshInterval() {
    // 只有在自动刷新正在运行时才更新间隔
    if (autoRefreshInterval) {
        // 清除现有的定时器
        clearInterval(autoRefreshInterval);
        
        // 获取新的间隔值
        const interval = parseInt(elements.refreshInterval.value) || 5;
        
        // 设置新的定时器
        autoRefreshInterval = setInterval(async () => {
            await refreshData();
        }, interval * 1000);
        
        // 显示消息
        showMessage(`自动刷新间隔已更新为${interval}秒`, 'success');
    }
}

// 更新欢迎标语
function updateWelcomeMessage() {
    const now = new Date();
    const hour = now.getHours();
    
    let greeting = '';
    if (hour >= 6 && hour < 12) {
        greeting = '早上好';
    } else if (hour >= 12 && hour < 14) {
        greeting = '中午好';
    } else if (hour >= 14 && hour < 18) {
        greeting = '下午好';
    } else if (hour >= 18 && hour < 22) {
        greeting = '晚上好';
    } else {
        greeting = '夜深了';
    }
    
    const messages = [
        `${greeting}，欢迎使用Modbus数据监控面板！`,
        `${greeting}，祝您工作愉快！`,
        `${greeting}，数据监控一切就绪！`,
        `${greeting}，系统运行正常！`
    ];
    
    // 随机选择一条欢迎信息
    const randomMessage = messages[Math.floor(Math.random() * messages.length)];
    elements.welcomeText.textContent = randomMessage;
}

// 启动北京时间显示
function startBeijingTime() {
    updateBeijingTime();
    setInterval(updateBeijingTime, 1000);
}

// 更新北京时间显示
function updateBeijingTime() {
    // 创建北京时间（UTC+8）
    const now = new Date();
    const beijingTime = new Date(now.getTime() + (now.getTimezoneOffset() * 60000) + (8 * 3600000));
    
    // 格式化时间显示
    const year = beijingTime.getFullYear();
    const month = String(beijingTime.getMonth() + 1).padStart(2, '0');
    const day = String(beijingTime.getDate()).padStart(2, '0');
    const hours = String(beijingTime.getHours()).padStart(2, '0');
    const minutes = String(beijingTime.getMinutes()).padStart(2, '0');
    const seconds = String(beijingTime.getSeconds()).padStart(2, '0');
    
    const timeString = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    elements.beijingTime.textContent = timeString;
}

// 连接服务器
async function connect() {
    const host = elements.serverIp.value;
    const port = parseInt(elements.serverPort.value);
    
    if (!host || !port) {
        showMessage('请输入服务器IP和端口', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/connect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ host, port })
        });
        
        const result = await response.json();
        
        if (result.success) {
            isConnected = true;
            elements.connectBtn.disabled = true;
            elements.disconnectBtn.disabled = false;
            elements.startRecordingBtn.disabled = false;
            elements.statusText.textContent = '已连接';
            elements.statusIndicator.className = 'status-indicator connected';
            showMessage('连接成功', 'success');
            
            // 连接成功后自动刷新一次数据
            refreshData();
        } else {
            showMessage('连接失败', 'error');
        }
    } catch (error) {
        showMessage('连接出错: ' + error.message, 'error');
    }
}

// 断开连接
async function disconnect() {
    try {
        const response = await fetch('/api/disconnect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            isConnected = false;
            elements.connectBtn.disabled = false;
            elements.disconnectBtn.disabled = true;
            elements.startRecordingBtn.disabled = true;
            elements.stopRecordingBtn.disabled = true;
            elements.statusText.textContent = '未连接';
            elements.statusIndicator.className = 'status-indicator disconnected';
            
            // 停止自动刷新
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
                autoRefreshInterval = null;
                elements.autoRefreshBtn.textContent = '开始自动刷新';
                elements.autoRefreshBtn.className = 'btn-secondary';
            }
            
            // 停止数据记录
            if (isRecording) {
                isRecording = false;
                elements.startRecordingBtn.disabled = false;
                elements.stopRecordingBtn.disabled = true;
                showMessage('连接断开，已停止数据记录', 'warning');
            }
            
            showMessage('已断开连接', 'info');
        } else {
            showMessage('断开连接失败', 'error');
        }
    } catch (error) {
        showMessage('断开连接出错: ' + error.message, 'error');
    }
}

// 刷新数据
async function refreshData() {
    if (!isConnected) {
        showMessage('请先连接到服务器', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        
        if (data.connected === false) {
            // 服务器连接已断开
            isConnected = false;
            elements.connectBtn.disabled = false;
            elements.disconnectBtn.disabled = true;
            elements.startRecordingBtn.disabled = true;
            elements.stopRecordingBtn.disabled = true;
            elements.statusText.textContent = '连接已断开';
            elements.statusIndicator.className = 'status-indicator disconnected';
            showMessage('服务器连接已断开', 'error');
            return;
        }
        
        if (data.board_data) {
            updateBoardData(data.board_data);
        }
        
        if (data.bms_data) {
            updateBmsData(data.bms_data);
        }
        
        updateSummaryData(data);
        updateChartData(data);
        
        // 如果正在记录数据，保存当前数据
        if (isRecording) {
            await saveCurrentData();
        }
    } catch (error) {
        showMessage('刷新数据失败: ' + error.message, 'error');
    }
}

// 更新二号板数据
function updateBoardData(data) {
    // 电源监测数据
    updateElement(elements.in1Current, data.IN1_current);
    updateElement(elements.in1Voltage, data.IN1_voltage?.toFixed(2));
    updateElement(elements.in2Current, data.IN2_current);
    updateElement(elements.in2Voltage, data.IN2_voltage?.toFixed(2));
    updateElement(elements.in3Current, data.IN3_current);
    updateElement(elements.in3Voltage, data.IN3_voltage?.toFixed(2));
    updateElement(elements.in4Current, data.IN4_current);
    updateElement(elements.in4Voltage, data.IN4_voltage?.toFixed(2));
    updateElement(elements.in5Current, data.IN5_current);
    updateElement(elements.in5Voltage, data.IN5_voltage?.toFixed(2));
    updateElement(elements.in6Current, data.IN6_current);
    updateElement(elements.in6Voltage, data.IN6_voltage?.toFixed(2));
    updateElement(elements.in7Current, data.IN7_current);
    updateElement(elements.in7Voltage, data.IN7_voltage?.toFixed(2));
    updateElement(elements.in8Current, data.IN8_current);
    updateElement(elements.in8Voltage, data.IN8_voltage?.toFixed(2));
    updateElement(elements.in9Current, data.IN9_current);
    updateElement(elements.in9Voltage, data.IN9_voltage?.toFixed(2));
    updateElement(elements.in10Current, data.IN10_current);
    updateElement(elements.in10Voltage, data.IN10_voltage?.toFixed(2));
    updateElement(elements.acCurrent, data.AC_current);
    updateElement(elements.vbatVoltage, data.VBAT_voltage?.toFixed(2));
    
    // 环境监测数据
    if (data.temperature_value !== undefined) {
        const tempValue = data.temperature_value;
        const tempText = tempValue >= 0 ? `+${tempValue}` : `${tempValue}`;
        updateElement(elements.temperature, tempText);
    }
    updateElement(elements.humidity, data.humidity);
    
    // 安全状态
    updateStatusElement(elements.doorStatus, data.door_status, {
        0: '关闭',
        1: '打开'
    });
    
    updateStatusElement(elements.waterStatus, data.water_status, {
        0: '无水',
        1: '有水'
    });
    
    updateStatusElement(elements.acStatus, data.ac_status, {
        0: '主电源',
        1: '备用电源'
    });
}

// 更新BMS数据
function updateBmsData(data) {
    // 电池电压
    updateElement(elements.battery1Voltage, data.battery1_voltage?.toFixed(3));
    updateElement(elements.battery2Voltage, data.battery2_voltage?.toFixed(3));
    updateElement(elements.battery3Voltage, data.battery3_voltage?.toFixed(3));
    updateElement(elements.battery4Voltage, data.battery4_voltage?.toFixed(3));
    updateElement(elements.battery5Voltage, data.battery5_voltage?.toFixed(3));
    updateElement(elements.battery6Voltage, data.battery6_voltage?.toFixed(3));
    updateElement(elements.battery7Voltage, data.battery7_voltage?.toFixed(3));
    updateElement(elements.battery8Voltage, data.battery8_voltage?.toFixed(3));
    
    // 系统参数
    updateElement(elements.totalVoltage, data.total_voltage?.toFixed(3));
    updateElement(elements.current, data.current?.toFixed(2));
    updateElement(elements.temperature1, data.temperature1?.toFixed(1));
    updateElement(elements.temperature2, data.temperature2?.toFixed(1));
    
    // 状态信息
    updateStatusElement(elements.balanceStatus, data.balance_status, {
        0: '未平衡',
        1: '正在平衡'
    });
    
    updateStatusElement(elements.chargeDischargeStatus, data.charge_discharge_status, {
        1: '充电',
        2: '放电',
        3: '空闲'
    });
    
    updateElement(elements.batteryPercentage, data.battery_percentage);
}

// 更新概览数据
function updateSummaryData(data) {
    if (data.board_data) {
        const boardData = data.board_data;
        updateElement(elements.summaryIn1Voltage, boardData.IN1_voltage?.toFixed(2));
        updateElement(elements.summaryIn4Voltage, boardData.IN4_voltage?.toFixed(2));
        updateElement(elements.summaryIn7Voltage, boardData.IN7_voltage?.toFixed(2));
        updateElement(elements.summaryIn10Voltage, boardData.IN10_voltage?.toFixed(2));
    }
    
    if (data.bms_data) {
        const bmsData = data.bms_data;
        updateElement(elements.summaryBattery1Voltage, bmsData.battery1_voltage?.toFixed(3));
        updateElement(elements.summaryBattery4Voltage, bmsData.battery4_voltage?.toFixed(3));
        updateElement(elements.summaryTotalVoltage, bmsData.total_voltage?.toFixed(3));
        updateElement(elements.summaryCurrent, bmsData.current?.toFixed(2));
        updateElement(elements.summaryBatteryPercentage, bmsData.battery_percentage);
    }
}

// 更新元素值并添加动画
function updateElement(element, value) {
    if (element && value !== undefined && value !== null) {
        // 只有当值真正改变时才触发动画
        if (element.textContent !== String(value)) {
            // 添加更新动画
            element.classList.remove('updated');
            // 使用setTimeout确保动画能够重新触发
            setTimeout(() => {
                element.classList.add('updated');
            }, 10);
            
            element.textContent = value;
        }
    }
}

// 更新状态元素
function updateStatusElement(element, value, statusMap) {
    if (element && value !== undefined && value !== null) {
        const statusText = statusMap[value] || value;
        
        // 只有当值真正改变时才触发动画
        if (element.textContent !== statusText) {
            element.textContent = statusText;
            
            // 添加更新动画
            element.classList.remove('updated');
            // 使用setTimeout确保动画能够重新触发
            setTimeout(() => {
                element.classList.add('updated');
            }, 10);
        }
    }
}

// 切换自动刷新
function toggleAutoRefresh() {
    if (!isConnected) {
        showMessage('请先连接到服务器', 'warning');
        return;
    }
    
    if (autoRefreshInterval) {
        // 停止自动刷新
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
        elements.autoRefreshBtn.textContent = '开始自动刷新';
        elements.autoRefreshBtn.className = 'btn-secondary';
        showMessage('已停止自动刷新', 'info');
    } else {
        // 开始自动刷新
        const interval = parseInt(elements.refreshInterval.value) || 5;
        autoRefreshInterval = setInterval(async () => {
            await refreshData();
        }, interval * 1000);
        elements.autoRefreshBtn.textContent = '停止自动刷新';
        elements.autoRefreshBtn.className = 'btn-primary';
        showMessage(`已开始自动刷新，间隔${interval}秒`, 'success');
    }
}

// 开始数据记录
async function startRecording() {
    if (!isConnected) {
        showMessage('请先连接到服务器', 'warning');
        return;
    }
    
    const recordingName = elements.recordingName.value || `记录_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}`;
    
    try {
        const response = await fetch('/api/start-recording', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: recordingName })
        });
        
        const result = await response.json();
        
        if (result.success) {
            isRecording = true;
            recordingId = result.recording_id;
            elements.startRecordingBtn.disabled = true;
            elements.stopRecordingBtn.disabled = false;
            elements.recordingName.value = '';
            
            // 显示记录状态信息
            showMessage(`开始数据记录: ${result.recording_name}`, 'success');
            
            // 更新记录状态显示
            updateRecordingStatus(result.recording_name, new Date());
        } else {
            showMessage('开始记录失败: ' + result.error, 'error');
        }
    } catch (error) {
        showMessage('开始记录出错: ' + error.message, 'error');
    }
}

// 更新记录状态显示
function updateRecordingStatus(name, startTime) {
    // 创建记录状态显示元素
    let recordingStatusEl = document.getElementById('recordingStatus');
    if (!recordingStatusEl) {
        recordingStatusEl = document.createElement('div');
        recordingStatusEl.id = 'recordingStatus';
        recordingStatusEl.className = 'recording-status-display';
        elements.recordingName.parentNode.insertBefore(recordingStatusEl, elements.recordingName.nextSibling);
    }
    
    // 格式化开始时间
    const timeString = startTime.toLocaleString('zh-CN');
    
    // 更新显示内容
    recordingStatusEl.innerHTML = `
        <div class="recording-info-display">
            <span class="recording-name">记录名称: ${name}</span>
            <span class="recording-time">开始时间: ${timeString}</span>
            <span class="recording-status">状态: 记录中...</span>
        </div>
    `;
}

// 停止数据记录
async function stopRecording() {
    try {
        const response = await fetch('/api/stop-recording', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            isRecording = false;
            recordingId = null;
            elements.startRecordingBtn.disabled = false;
            elements.stopRecordingBtn.disabled = true;
            
            // 移除记录状态显示
            const recordingStatusEl = document.getElementById('recordingStatus');
            if (recordingStatusEl) {
                recordingStatusEl.remove();
            }
            
            showMessage('数据记录已停止', 'success');
        } else {
            showMessage('停止记录失败: ' + result.error, 'error');
        }
    } catch (error) {
        showMessage('停止记录出错: ' + error.message, 'error');
    }
}

// 保存当前数据
async function saveCurrentData() {
    try {
        const response = await fetch('/api/save-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (!result.success) {
            console.error('保存数据失败:', result.error);
            showMessage('保存数据失败: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('保存数据出错:', error);
        showMessage('保存数据出错: ' + error.message, 'error');
    }
}

// 更新日志
async function updateLogs() {
    try {
        const response = await fetch('/api/logs');
        const logs = await response.json();
        
        if (logs && logs.length > 0) {
            elements.logContent.innerHTML = '';
            // 显示最新的20条日志
            const displayLogs = logs.slice(-20);
            displayLogs.forEach(log => {
                const logDiv = document.createElement('div');
                logDiv.textContent = log;
                elements.logContent.appendChild(logDiv);
            });
            // 滚动到底部
            elements.logContent.scrollTop = elements.logContent.scrollHeight;
        }
    } catch (error) {
        console.error('更新日志失败:', error);
    }
}

// 清除日志
async function clearLogs() {
    try {
        const response = await fetch('/api/logs/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            elements.logContent.innerHTML = '';
            showMessage('日志已清除', 'success');
        } else {
            showMessage('清除日志失败', 'error');
        }
    } catch (error) {
        showMessage('清除日志出错: ' + error.message, 'error');
    }
}

// 显示消息
function showMessage(message, type) {
    // 创建消息元素
    const messageEl = document.createElement('div');
    messageEl.className = `message message-${type}`;
    messageEl.textContent = message;
    
    // 添加到页面
    document.body.appendChild(messageEl);
    
    // 3秒后移除
    setTimeout(() => {
        if (messageEl.parentNode) {
            messageEl.parentNode.removeChild(messageEl);
        }
    }, 3000);
}

// 启动连接检查
function startConnectionCheck() {
    connectionCheckInterval = setInterval(checkConnectionStatus, 5000); // 每5秒检查一次
}

// 检查连接状态
async function checkConnectionStatus() {
    try {
        const response = await fetch('/api/connection-status');
        const status = await response.json();
        
        // 更新UI状态
        if (status.connected !== isConnected) {
            isConnected = status.connected;
            if (isConnected) {
                elements.connectBtn.disabled = true;
                elements.disconnectBtn.disabled = false;
                elements.startRecordingBtn.disabled = false;
                elements.statusText.textContent = '已连接';
                elements.statusIndicator.className = 'status-indicator connected';
            } else {
                elements.connectBtn.disabled = false;
                elements.disconnectBtn.disabled = true;
                elements.startRecordingBtn.disabled = true;
                elements.stopRecordingBtn.disabled = true;
                elements.statusText.textContent = '连接已断开';
                elements.statusIndicator.className = 'status-indicator disconnected';
                
                // 停止自动刷新
                if (autoRefreshInterval) {
                    clearInterval(autoRefreshInterval);
                    autoRefreshInterval = null;
                    elements.autoRefreshBtn.textContent = '开始自动刷新';
                    elements.autoRefreshBtn.className = 'btn-secondary';
                }
                
                // 停止数据记录
                if (isRecording) {
                    isRecording = false;
                    showMessage('检测到服务器连接已断开，已停止数据记录', 'error');
                }
                
                showMessage('检测到服务器连接已断开', 'error');
            }
        }
    } catch (error) {
        console.error('检查连接状态失败:', error);
    }
}

// 启动日志更新
function startLogUpdate() {
    setInterval(updateLogs, 2000); // 每2秒更新一次日志
    updateLogs(); // 立即更新一次
}

// 初始化图表
function initChart() {
    const ctx = document.getElementById('dataChart').getContext('2d');
    dataChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '数据值',
                data: [],
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                tension: 0.1,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: '时间'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: '数值'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

// 更新图表数据
function updateChartData(data) {
    if (!dataChart) return;
    
    const selectedType = elements.chartDataType.value;
    let value = null;
    let label = '';
    
    // 根据选择的数据类型获取对应值
    switch (selectedType) {
        case 'in1_current':
            value = data.board_data?.IN1_current;
            label = 'IN1电流 (mA)';
            break;
        case 'in1_voltage':
            value = data.board_data?.IN1_voltage;
            label = 'IN1电压 (V)';
            break;
        case 'in2_current':
            value = data.board_data?.IN2_current;
            label = 'IN2电流 (mA)';
            break;
        case 'in2_voltage':
            value = data.board_data?.IN2_voltage;
            label = 'IN2电压 (V)';
            break;
        case 'in3_current':
            value = data.board_data?.IN3_current;
            label = 'IN3电流 (mA)';
            break;
        case 'in3_voltage':
            value = data.board_data?.IN3_voltage;
            label = 'IN3电压 (V)';
            break;
        case 'in4_current':
            value = data.board_data?.IN4_current;
            label = 'IN4电流 (mA)';
            break;
        case 'in4_voltage':
            value = data.board_data?.IN4_voltage;
            label = 'IN4电压 (V)';
            break;
        case 'in5_current':
            value = data.board_data?.IN5_current;
            label = 'IN5电流 (mA)';
            break;
        case 'in5_voltage':
            value = data.board_data?.IN5_voltage;
            label = 'IN5电压 (V)';
            break;
        case 'in6_current':
            value = data.board_data?.IN6_current;
            label = 'IN6电流 (mA)';
            break;
        case 'in6_voltage':
            value = data.board_data?.IN6_voltage;
            label = 'IN6电压 (V)';
            break;
        case 'in7_current':
            value = data.board_data?.IN7_current;
            label = 'IN7电流 (mA)';
            break;
        case 'in7_voltage':
            value = data.board_data?.IN7_voltage;
            label = 'IN7电压 (V)';
            break;
        case 'in8_current':
            value = data.board_data?.IN8_current;
            label = 'IN8电流 (mA)';
            break;
        case 'in8_voltage':
            value = data.board_data?.IN8_voltage;
            label = 'IN8电压 (V)';
            break;
        case 'in9_current':
            value = data.board_data?.IN9_current;
            label = 'IN9电流 (mA)';
            break;
        case 'in9_voltage':
            value = data.board_data?.IN9_voltage;
            label = 'IN9电压 (V)';
            break;
        case 'in10_current':
            value = data.board_data?.IN10_current;
            label = 'IN10电流 (mA)';
            break;
        case 'in10_voltage':
            value = data.board_data?.IN10_voltage;
            label = 'IN10电压 (V)';
            break;
        case 'ac_current':
            value = data.board_data?.AC_current;
            label = 'AC电流 (A)';
            break;
        case 'vbat_voltage':
            value = data.board_data?.VBAT_voltage;
            label = 'VBAT电压 (V)';
            break;
        case 'battery1_voltage':
            value = data.bms_data?.battery1_voltage;
            label = '电池1电压 (V)';
            break;
        case 'battery2_voltage':
            value = data.bms_data?.battery2_voltage;
            label = '电池2电压 (V)';
            break;
        case 'battery3_voltage':
            value = data.bms_data?.battery3_voltage;
            label = '电池3电压 (V)';
            break;
        case 'battery4_voltage':
            value = data.bms_data?.battery4_voltage;
            label = '电池4电压 (V)';
            break;
        case 'battery5_voltage':
            value = data.bms_data?.battery5_voltage;
            label = '电池5电压 (V)';
            break;
        case 'battery6_voltage':
            value = data.bms_data?.battery6_voltage;
            label = '电池6电压 (V)';
            break;
        case 'battery7_voltage':
            value = data.bms_data?.battery7_voltage;
            label = '电池7电压 (V)';
            break;
        case 'battery8_voltage':
            value = data.bms_data?.battery8_voltage;
            label = '电池8电压 (V)';
            break;
        case 'total_voltage':
            value = data.bms_data?.total_voltage;
            label = '总电压 (V)';
            break;
        case 'current':
            value = data.bms_data?.current;
            label = '电流 (A)';
            break;
        case 'temperature1':
            value = data.bms_data?.temperature1;
            label = '温度1 (℃)';
            break;
        case 'temperature2':
            value = data.bms_data?.temperature2;
            label = '温度2 (℃)';
            break;
        case 'temperature':
            value = data.board_data?.temperature_value;
            label = '环境温度 (℃)';
            break;
        case 'humidity':
            value = data.board_data?.humidity;
            label = '湿度 (%RH)';
            break;
    }
    
    if (value !== null && value !== undefined) {
        // 初始化数据数组
        if (!chartData[selectedType]) {
            chartData[selectedType] = {
                labels: [],
                values: []
            };
        }
        
        // 获取当前时间
        const now = new Date();
        const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
        
        // 添加新数据点
        chartData[selectedType].labels.push(timeString);
        chartData[selectedType].values.push(value);
        
        // 限制数据点数量，最多保留100个点
        if (chartData[selectedType].labels.length > 100) {
            chartData[selectedType].labels.shift();
            chartData[selectedType].values.shift();
        }
        
        // 更新图表
        updateChart();
    }
}

// 更新图表显示
function updateChart() {
    if (!dataChart) return;
    
    const selectedType = elements.chartDataType.value;
    const data = chartData[selectedType];
    
    if (data) {
        // 更新数据集标签
        let label = '';
        switch (selectedType) {
            case 'in1_voltage': label = 'IN1电压 (V)'; break;
            case 'in4_voltage': label = 'IN4电压 (V)'; break;
            case 'in7_voltage': label = 'IN7电压 (V)'; break;
            case 'in10_voltage': label = 'IN10电压 (V)'; break;
            case 'battery1_voltage': label = '电池1电压 (V)'; break;
            case 'battery4_voltage': label = '电池4电压 (V)'; break;
            case 'total_voltage': label = '总电压 (V)'; break;
            case 'current': label = '电流 (A)'; break;
            case 'temperature': label = '温度 (℃)'; break;
            case 'humidity': label = '湿度 (%RH)'; break;
        }
        
        // 更新图表数据
        dataChart.data.datasets[0].label = label;
        dataChart.data.labels = data.labels;
        dataChart.data.datasets[0].data = data.values;
        dataChart.update();
    }
}

// 清除图表
function clearChart() {
    const selectedType = elements.chartDataType.value;
    if (chartData[selectedType]) {
        chartData[selectedType].labels = [];
        chartData[selectedType].values = [];
        updateChart();
        showMessage('图表数据已清除', 'success');
    }
}

// 全局变量用于控制扫描过程
let scanAbortController = null;
let isScanning = false;
let scannedCount = 0;
let totalCount = 0;

// 扫描网络中的Modbus设备
async function scanDevices() {
    // 如果已经在扫描，直接返回
    if (isScanning) return;
    
    // 显示扫描进度
    elements.scanResultsContainer.style.display = 'block';
    elements.scanProgress.style.display = 'block';
    elements.scanResultsList.innerHTML = '';
    
    // 显示停止扫描按钮
    elements.scanDevicesBtn.style.display = 'none';
    elements.stopScanBtn.style.display = 'inline-block';
    
    // 初始化扫描控制
    isScanning = true;
    scanAbortController = new AbortController();
    scannedCount = 0;
    
    // 更新进度文本
    updateScanProgress();
    
    try {
        const response = await fetch('/api/scan-devices', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                network: '192.168.1.0/24', // 默认网络范围
                port: 502, // 默认Modbus端口
                timeout: 1, // 减少超时时间以加快扫描
                max_workers: 100 // 增加并发数以加快扫描
            }),
            signal: scanAbortController.signal
        });
        
        const result = await response.json();
        
        // 隐藏进度条
        elements.scanProgress.style.display = 'none';
        
        // 恢复扫描按钮
        elements.scanDevicesBtn.style.display = 'inline-block';
        elements.stopScanBtn.style.display = 'none';
        isScanning = false;
        
        if (result.success) {
            if (result.devices.length > 0) {
                // 显示扫描结果
                result.devices.forEach(device => {
                    const deviceElement = document.createElement('div');
                    deviceElement.className = 'scan-result-item';
                    deviceElement.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px; border-bottom: 1px solid #eee;">
                            <div>
                                <strong>${device.ip}</strong>
                                <span style="margin-left: 10px; color: #666;">端口: ${device.port}</span>
                            </div>
                            <button class="btn-secondary btn-sm" onclick="selectDevice('${device.ip}', ${device.port})" style="padding: 4px 8px; font-size: 12px;">
                                <i class="fas fa-check"></i> 选择
                            </button>
                        </div>
                    `;
                    elements.scanResultsList.appendChild(deviceElement);
                });
                
                showMessage(`扫描完成，发现 ${result.devices.length} 个设备`, 'success');
            } else {
                elements.scanResultsList.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">未发现Modbus设备</p>';
                showMessage('扫描完成，未发现设备', 'info');
            }
        } else {
            elements.scanResultsList.innerHTML = `<p style="color: red; text-align: center; padding: 20px;">扫描失败: ${result.error}</p>`;
            showMessage(`扫描失败: ${result.error}`, 'error');
        }
    } catch (error) {
        // 检查是否是用户主动停止扫描
        if (error.name === 'AbortError') {
            elements.scanResultsList.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">扫描已停止</p>';
            showMessage('扫描已停止', 'info');
        } else {
            // 隐藏进度条
            elements.scanProgress.style.display = 'none';
            elements.scanResultsList.innerHTML = `<p style="color: red; text-align: center; padding: 20px;">扫描出错: ${error.message}</p>`;
            showMessage(`扫描出错: ${error.message}`, 'error');
        }
        
        // 恢复扫描按钮
        elements.scanDevicesBtn.style.display = 'inline-block';
        elements.stopScanBtn.style.display = 'none';
        isScanning = false;
    }
}

// 更新扫描进度显示
function updateScanProgress() {
    if (isScanning) {
        elements.scanProgressText.textContent = `${scannedCount}/254`;
        setTimeout(updateScanProgress, 100); // 每100毫秒更新一次
    }
}

// 停止扫描设备
function stopScanDevices() {
    if (isScanning && scanAbortController) {
        scanAbortController.abort();
        isScanning = false;
        
        // 恢复按钮状态
        elements.scanDevicesBtn.style.display = 'inline-block';
        elements.stopScanBtn.style.display = 'none';
        
        // 更新界面
        elements.scanProgress.style.display = 'none';
        elements.scanResultsList.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">扫描已停止</p>';
        
        showMessage('正在停止扫描...', 'info');
    }
}

// 选择设备并填充到连接配置中
function selectDevice(ip, port) {
    elements.serverIp.value = ip;
    elements.serverPort.value = port;
    showMessage(`已选择设备: ${ip}:${port}`, 'success');
    
    // 自动滚动到连接配置区域
    document.querySelector('.config-panel').scrollIntoView({ behavior: 'smooth' });
}

// 页面可见性变化时处理
document.addEventListener('visibilitychange', function() {
    if (document.hidden && autoRefreshInterval) {
        // 页面隐藏时停止自动刷新
        clearInterval(autoRefreshInterval);
    } else if (!document.hidden && autoRefreshInterval) {
        // 页面显示时重新开始自动刷新
        const interval = parseInt(elements.refreshInterval.value) || 5;
        autoRefreshInterval = setInterval(refreshData, interval * 1000);
    }
});

// 页面卸载时清理
window.addEventListener('beforeunload', function() {
    if (connectionCheckInterval) {
        clearInterval(connectionCheckInterval);
    }
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
});

// 初始化应用
document.addEventListener('DOMContentLoaded', initApp);

// 在DOMContentLoaded事件监听器之后添加
document.addEventListener('DOMContentLoaded', function() {
    // 确保扫描结果容器在页面加载时是隐藏的
    if (elements.scanResultsContainer) {
        elements.scanResultsContainer.style.display = 'none';
    }
});

// 添加清除日志按钮事件监听器
document.addEventListener('DOMContentLoaded', function() {
    const clearLogsBtn = document.createElement('button');
    clearLogsBtn.className = 'btn btn-secondary';
    clearLogsBtn.textContent = '清除日志';
    clearLogsBtn.addEventListener('click', clearLogs);
    
    // 将清除日志按钮添加到日志面板的按钮组中
    const logPanel = document.querySelector('.log-panel');
    if (logPanel) {
        const buttonGroup = logPanel.querySelector('.button-group');
        if (buttonGroup) {
            buttonGroup.appendChild(clearLogsBtn);
        } else {
            const newButtonGroup = document.createElement('div');
            newButtonGroup.className = 'button-group';
            newButtonGroup.appendChild(clearLogsBtn);
            logPanel.insertBefore(newButtonGroup, logPanel.querySelector('.log-container'));
        }
    }
});