#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modbus RTU 主站工具（适配版）
功能：支持 01/02/03/04（读）、05/06/15/16（写），串口收发，日志保存，数据可视化
适配：优化窗口尺寸/布局，兼容1080P/768P屏幕，最大化无错乱
"""
import sys
import time
import serial
import serial.tools.list_ports
from typing import List, Tuple, Optional, Dict, Set, Union
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QPushButton, QTextEdit, QCheckBox, QLabel, QMessageBox,
    QGroupBox, QGridLayout, QStatusBar, QLineEdit, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
)
from PyQt5.QtCore import (
    QThread, pyqtSignal, Qt, QTimer, QDateTime, QMutex, QMutexLocker,
    QThreadPool, QRunnable, pyqtSlot
)
from PyQt5.QtGui import QFont, QColor, QClipboard, QPalette

# ===================== 全局常量/枚举（适配优化） =====================
MODBUS_ERROR_CODES: Dict[int, str] = {
    0x01: "非法功能码",
    0x02: "非法数据地址",
    0x03: "非法数据值",
    0x04: "从站设备故障",
    0x05: "确认",
    0x06: "从站设备忙",
    0x07: "否定确认",
    0x08: "内存奇偶校验错误"
}

FUNC_CODE_MAP: Dict[int, Tuple[str, str, str, Tuple[int, int]]] = {
    1: ("读线圈", "read", "Read Coils", (0, 65535)),
    2: ("读离散输入", "read", "Read Discrete Inputs", (0, 65535)),
    3: ("读保持寄存器", "read", "Read Holding Registers", (0, 65535)),
    4: ("读输入寄存器", "read", "Read Input Registers", (0, 65535)),
    5: ("写单线圈", "write", "Write Single Coil", (0, 65535)),
    6: ("写单寄存器", "write", "Write Single Register", (0, 65535)),
    15: ("写多线圈", "write", "Write Multiple Coils", (0, 65535)),
    16: ("写多寄存器", "write", "Write Multiple Registers", (0, 65535))
}

DISPLAY_MODE_MAP: Dict[str, str] = {
    "十进制": "dec",
    "十六进制": "hex",
    "二进制": "bin"
}

DEFAULT_SERIAL_PARAMS = {
    "baudrate": 9600,
    "databits": 8,
    "stopbits": 1.0,
    "parity": serial.PARITY_NONE,
    "rtscts": False,
    "timeout": 0.1
}

# 字体适配：降低字号，适配通用屏幕
FONT_CONFIG = {
    "default": QFont("Microsoft YaHei", 8),  # 原14 → 12
    "mono": QFont("Consolas", 8),  # 原14 → 12
    "title": QFont("Microsoft YaHei", 8, QFont.Bold),  # 原16 → 14
    "status": QFont("Microsoft YaHei", 8)  # 原14 → 12
}


# ===================== 工具函数 =====================
def modbus_crc16(data: bytes) -> bytes:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 0x0001 else crc >> 1
    return bytes([crc & 0xFF, (crc >> 8) & 0xFF])


def validate_numeric_input(text: str, min_val: int = 0, max_val: int = 65535, field_name: str = "值") -> Optional[int]:
    try:
        val = int(text.strip())
        if min_val <= val <= max_val:
            return val
        QMessageBox.warning(None, "输入错误", f"{field_name}需在 {min_val}-{max_val} 之间")
        return None
    except ValueError:
        QMessageBox.warning(None, "输入错误", f"{field_name}请输入有效的整数")
        return None


def validate_modbus_addr(func_code: int, addr: int) -> bool:
    min_addr, max_addr = FUNC_CODE_MAP[func_code][3]
    if not (min_addr <= addr <= max_addr):
        QMessageBox.warning(None, "地址错误",
                            f"{FUNC_CODE_MAP[func_code][0]}的地址范围为 {min_addr}-{max_addr}")
        return False
    return True


def format_value(val: Union[int, bool], mode: str) -> str:
    if isinstance(val, bool):
        return "1" if val else "0"
    if mode == "hex":
        return f"0x{val:04X}"
    elif mode == "bin":
        return f"0b{val:016b}"
    return str(val)


def parse_write_values(text: str, func_code: int, count: int) -> Optional[List[Union[int, bool]]]:
    try:
        values = [v.strip() for v in text.split(",") if v.strip()]
        write_values = []

        if func_code in [5, 6] and len(values) != 1:
            raise Exception(f"{FUNC_CODE_MAP[func_code][0]}仅支持单个值")
        if func_code in [15, 16] and len(values) < count:
            raise Exception(f"{FUNC_CODE_MAP[func_code][0]}需输入{count}个值（当前{len(values)}个）")

        for idx, val in enumerate(values[:count]):
            if func_code in [5, 15]:
                if val.lower() in ["1", "true", "on"]:
                    write_values.append(True)
                elif val.lower() in ["0", "false", "off"]:
                    write_values.append(False)
                else:
                    raise Exception(f"线圈值{idx + 1}需为 0/1/True/False")
            else:
                int_val = int(val)
                if not (0 <= int_val <= 65535):
                    raise Exception(f"寄存器值{idx + 1}需在 0-65535 之间")
                write_values.append(int_val)

        return write_values
    except Exception as e:
        QMessageBox.warning(None, "写值解析失败", str(e))
        return None


def scan_valid_ports() -> List[str]:
    valid_ports: Set[str] = set()
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if port.device and not any(filter_word in port.description.lower()
                                   for filter_word in ["bluetooth", "蓝牙", "virtual", "虚拟"]):
            port_name = f"{port.device} - {port.description}"
            valid_ports.add(port_name)
    return sorted(list(valid_ports))


# ===================== 串口接收线程 =====================
class SerialReceiveThread(QThread):
    receive_signal = pyqtSignal(bytes)
    error_signal = pyqtSignal(str)

    def __init__(self, serial_obj: serial.Serial):
        super().__init__()
        self.serial = serial_obj
        self._is_running = False
        self._mutex = QMutex()
        self.setPriority(QThread.LowPriority)

    def run(self) -> None:
        with QMutexLocker(self._mutex):
            self._is_running = True

        while True:
            with QMutexLocker(self._mutex):
                if not self._is_running or not self.serial.is_open:
                    break

            try:
                if self.serial.in_waiting > 0:
                    data = self.serial.read(self.serial.in_waiting)
                    self.receive_signal.emit(data)
                time.sleep(0.005)
            except Exception as e:
                self.error_signal.emit(f"接收异常：{str(e)}")
                break

    def stop(self) -> None:
        with QMutexLocker(self._mutex):
            self._is_running = False
        if not self.wait(2000):
            self.terminate()
            self.wait()


# ===================== Modbus 操作线程 =====================
class ModbusThread(QThread):
    poll_result = pyqtSignal(list, int, int)
    status_update = pyqtSignal(str)
    log_update = pyqtSignal(str, str)
    write_result = pyqtSignal(bool, str)

    def __init__(self, serial_obj: serial.Serial):
        super().__init__()
        self.serial = serial_obj
        self._is_running = False
        self._mutex = QMutex()
        self.slave_id: int = 1
        self.func_code: int = 3
        self.start_addr: int = 0
        self.count: int = 10
        self.interval: int = 1000
        self.write_values: List[Union[int, bool]] = []
        self.is_write_op: bool = False
        self.tx_count: int = 0
        self.err_count: int = 0

    def set_read_params(self, slave_id: int, func_code: int, start_addr: int, count: int, interval: int) -> None:
        with QMutexLocker(self._mutex):
            self.slave_id = slave_id
            self.func_code = func_code
            self.start_addr = start_addr
            self.count = min(count, 1000)
            self.interval = interval
            self.is_write_op = False
            self.tx_count = 0
            self.err_count = 0

    def set_write_params(self, slave_id: int, func_code: int, start_addr: int, count: int,
                         values: List[Union[int, bool]]) -> None:
        with QMutexLocker(self._mutex):
            self.slave_id = slave_id
            self.func_code = func_code
            self.start_addr = start_addr
            self.count = min(count, 1000)
            self.write_values = values[:self.count]
            self.is_write_op = True
            self.tx_count = 0
            self.err_count = 0

    def run(self) -> None:
        with QMutexLocker(self._mutex):
            self._is_running = True

        try:
            if self.is_write_op:
                self._execute_write()
            else:
                self._execute_read_loop()
        except Exception as e:
            err_msg = f"操作异常：{str(e)}"
            self.status_update.emit(err_msg)
            self.log_update.emit("Modbus-错误", err_msg)

        with QMutexLocker(self._mutex):
            self._is_running = False

    def _execute_read_loop(self) -> None:
        while True:
            with QMutexLocker(self._mutex):
                if not self._is_running or not self.serial.is_open:
                    break

            self._execute_read_once()
            sleep_steps = int(self.interval / 10)
            for _ in range(sleep_steps):
                time.sleep(0.01)
                with QMutexLocker(self._mutex):
                    if not self._is_running:
                        break

    def _execute_read_once(self) -> None:
        try:
            req_data = self._build_read_request()
            if not req_data:
                return

            self.serial.write(req_data)
            self.tx_count += 1
            self.log_update.emit("Modbus-发送",
                                 f"从站{self.slave_id} 功能码{self.func_code:02X} | {req_data.hex(' ')}")

            time.sleep(0.01 + (len(req_data) * 10) / self.serial.baudrate)
            if self.serial.in_waiting == 0:
                raise Exception("从站无响应")

            resp_data = self.serial.read(self.serial.in_waiting)
            self.log_update.emit("Modbus-接收",
                                 f"从站{self.slave_id} | {resp_data.hex(' ')}")

            self._validate_response(resp_data)
            data_list = self._parse_response(resp_data)
            self.poll_result.emit(data_list, self.tx_count, self.err_count)
            self.status_update.emit(f"读成功：{self.count}个{FUNC_CODE_MAP[self.func_code][0]}")
        except Exception as e:
            self.err_count += 1
            err_msg = f"读失败：{str(e)}"
            self.status_update.emit(err_msg)
            self.log_update.emit("Modbus-错误",
                                 f"{err_msg} | Tx={self.tx_count} Err={self.err_count}")
            self.poll_result.emit([], self.tx_count, self.err_count)

    def _execute_write(self) -> None:
        try:
            req_data = self._build_write_request()
            if not req_data:
                return

            self.serial.write(req_data)
            self.tx_count += 1
            self.log_update.emit("Modbus-发送",
                                 f"从站{self.slave_id} 功能码{self.func_code:02X} | {req_data.hex(' ')}")

            time.sleep(0.01 + (len(req_data) * 10) / self.serial.baudrate)
            if self.serial.in_waiting == 0:
                raise Exception("从站无响应")

            resp_data = self.serial.read(self.serial.in_waiting)
            self.log_update.emit("Modbus-接收",
                                 f"从站{self.slave_id} | {resp_data.hex(' ')}")

            self._validate_write_response(req_data, resp_data)
            success_msg = f"写成功：{self.count}个{FUNC_CODE_MAP[self.func_code][0]}"
            self.write_result.emit(True, success_msg)
            self.status_update.emit(success_msg)
            self.poll_result.emit([], self.tx_count, self.err_count)
        except Exception as e:
            self.err_count += 1
            err_msg = f"写失败：{str(e)}"
            self.status_update.emit(err_msg)
            self.log_update.emit("Modbus-错误",
                                 f"{err_msg} | Tx={self.tx_count} Err={self.err_count}")
            self.write_result.emit(False, err_msg)
            self.poll_result.emit([], self.tx_count, self.err_count)

    def _build_read_request(self) -> Optional[bytearray]:
        try:
            req = bytearray([self.slave_id, self.func_code])
            req.extend(self.start_addr.to_bytes(2, 'big'))
            req.extend(self.count.to_bytes(2, 'big'))
            req.extend(modbus_crc16(req))
            return req
        except Exception as e:
            err_msg = f"读报文组装失败：{str(e)}"
            self.status_update.emit(err_msg)
            self.log_update.emit("Modbus-错误", err_msg)
            return None

    def _build_write_request(self) -> Optional[bytearray]:
        try:
            req = bytearray([self.slave_id, self.func_code])
            if self.func_code == 5:
                req.extend(self.start_addr.to_bytes(2, 'big'))
                req.extend((0xFF00 if self.write_values[0] else 0x0000).to_bytes(2, 'big'))
            elif self.func_code == 6:
                req.extend(self.start_addr.to_bytes(2, 'big'))
                req.extend(int(self.write_values[0]).to_bytes(2, 'big'))
            elif self.func_code == 15:
                req.extend(self.start_addr.to_bytes(2, 'big'))
                req.extend(self.count.to_bytes(2, 'big'))
                byte_count = (self.count + 7) // 8
                req.append(byte_count)
                coil_bytes = bytearray(byte_count)
                for idx, val in enumerate(self.write_values[:self.count]):
                    if val:
                        coil_bytes[idx // 8] |= 1 << (idx % 8)
                req.extend(coil_bytes)
            elif self.func_code == 16:
                req.extend(self.start_addr.to_bytes(2, 'big'))
                req.extend(self.count.to_bytes(2, 'big'))
                req.append(self.count * 2)
                for val in self.write_values[:self.count]:
                    req.extend(int(val).to_bytes(2, 'big'))
            else:
                raise Exception(f"不支持的写功能码：{self.func_code}")

            req.extend(modbus_crc16(req))
            return req
        except Exception as e:
            err_msg = f"写报文组装失败：{str(e)}"
            self.status_update.emit(err_msg)
            self.log_update.emit("Modbus-错误", err_msg)
            return None

    def _validate_response(self, resp_data: bytes) -> None:
        if len(resp_data) < 5:
            raise Exception("响应数据过短（小于5字节）")

        resp_crc = resp_data[-2:]
        calc_crc = modbus_crc16(resp_data[:-2])
        if resp_crc != calc_crc:
            raise Exception(f"CRC校验失败（接收：{resp_crc.hex()} 计算：{calc_crc.hex()}）")

        if resp_data[1] == self.func_code + 0x80:
            err_code = resp_data[2]
            raise Exception(f"从站异常：{MODBUS_ERROR_CODES.get(err_code, f'未知错误{err_code:02X}')}")

        if resp_data[1] != self.func_code:
            raise Exception(f"功能码不匹配（接收：{resp_data[1]} 预期：{self.func_code}）")

    def _validate_write_response(self, req_data: bytes, resp_data: bytes) -> None:
        if len(resp_data) < 5:
            raise Exception("响应数据过短（小于5字节）")

        resp_crc = resp_data[-2:]
        calc_crc = modbus_crc16(resp_data[:-2])
        if resp_crc != calc_crc:
            raise Exception(f"CRC校验失败（接收：{resp_crc.hex()} 计算：{calc_crc.hex()}）")

        if self.func_code in [5, 6]:
            if resp_data != req_data:
                raise Exception("写响应与请求不匹配")
        elif self.func_code in [15, 16]:
            resp_addr = int.from_bytes(resp_data[2:4], 'big')
            resp_count = int.from_bytes(resp_data[4:6], 'big')
            if resp_addr != self.start_addr or resp_count != self.count:
                raise Exception(f"地址/数量不匹配（地址：{resp_addr}≠{self.start_addr} 数量：{resp_count}≠{self.count}）")

    def _parse_response(self, resp_data: bytes) -> List[Union[int, bool]]:
        data_list = []
        if self.func_code in [1, 2]:
            byte_count = resp_data[2]
            for idx in range(self.count):
                if idx >= byte_count * 8:
                    data_list.append(False)
                else:
                    data_list.append((resp_data[3 + idx // 8] & (1 << (idx % 8))) != 0)
        elif self.func_code in [3, 4]:
            for i in range(self.count):
                if i * 2 + 3 >= len(resp_data) - 2:
                    data_list.append(0)
                else:
                    data_list.append(int.from_bytes(resp_data[3 + i * 2: 5 + i * 2], 'big'))
        return data_list

    def stop(self) -> None:
        with QMutexLocker(self._mutex):
            self._is_running = False
        if not self.wait(2000):
            self.terminate()
            self.wait()


# ===================== 主窗口（布局适配优化） =====================
class ModbusRTUMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modbus RTU 主站工具（适配版）")
        # 初始尺寸适配1080P（原1800x1100 → 1200x800）
        self.setGeometry(100, 100, 1200, 800)
        # 最小尺寸适配768P（原1600x1000 → 800x600）
        self.setMinimumSize(800, 600)

        self._setup_global_style()
        self.serial: serial.Serial = serial.Serial()
        self.receive_thread: Optional[SerialReceiveThread] = None
        self.modbus_thread: Optional[ModbusThread] = None

        self.loop_send_timer = QTimer()
        self.loop_send_timer.timeout.connect(self.send_data)
        self.port_scan_timer = QTimer()
        self.port_scan_timer.timeout.connect(self.scan_serial_ports)
        self.port_scan_timer.start(2000)

        self.is_serial_open: bool = False
        self.is_loop_sending: bool = False
        self.display_mode: str = "dec"
        self.total_receive_bytes: int = 0
        self.session_receive_bytes: int = 0

        self._init_ui()
        self.show()

    def _setup_global_style(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(245, 245, 245))
        palette.setColor(QPalette.WindowText, QColor(50, 50, 50))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
        palette.setColor(QPalette.Button, QColor(230, 230, 230))
        palette.setColor(QPalette.ButtonText, QColor(50, 50, 50))
        self.setPalette(palette)

        # 样式表适配：降低控件尺寸，优化最大化布局
        self.setStyleSheet("""
            QMainWindow {background: #F5F5F5;}
            QGroupBox {
                font-weight: bold;
                font-size: 10px;  /* 原16 → 14 */
                border: 1px solid #DDD;
                border-radius: 6px;
                margin-top: 6px;   /* 原12 → 8 */
                padding-top: 6px;  /* 原10 → 8 */
            }
            QPushButton {
                background: #E8E8E8;
                border: 1px solid #CCC;
                border-radius: 6px;
                padding: 6px 14px; /* 原10px20px → 8px16px */
                font-size: 6px;   /* 原14 → 12 */
                min-height: 20px;  /* 原40 → 35 */
                sizePolicy: Expanding;
            }
            QPushButton:hover {background: #D8D8D8;}
            QPushButton:disabled {background: #F0F0F0; color: #999;}
            QPushButton#primaryBtn {
                background: #4A90E2;
                color: white;
                border: none;
                min-height: 25px; /* 原45 → 40 */
            }
            QPushButton#primaryBtn:hover {background: #357ABD;}
            QLabel {font-size: 10px; color: #333;} /* 原14 → 12 */
            QTableWidget {
                gridline-color: #DDD;
                font-family: Consolas;
                font-size: 10px;   /* 原14 → 12 */
                border: 1px solid #EEE;
                border-radius: 4px;
                min-height: 200px; /* 原500 → 300 */
                sizePolicy: Expanding;
            }
            QTableWidget::item:selected {
                background: #E1F0FF;
                color: #333;
            }
            QStatusBar {font-size: 10px; color: #333; background: #F0F0F0;} /* 原14 → 12 */
            QLineEdit, QComboBox, QTextEdit {
                border: 1px solid #CCC;
                border-radius: 4px;
                padding: 4px 8px; /* 原6px10px → 4px8px */
                font-size: 10px;  /* 原14 → 12 */
                min-height: 20px; /* 原35 → 30 */
                sizePolicy: Expanding;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 1px solid #4A90E2;
                outline: none;
            }
        """)

    def _init_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        # 布局间距适配（原20 → 12，原25 → 15）
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        main_layout.addWidget(self._build_serial_config_widget())
        main_layout.addWidget(self._build_modbus_config_widget())
        # 优化拉伸权重，最大化时合理分配空间
        main_layout.addWidget(self._build_io_widget(), stretch=1)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setFont(FONT_CONFIG["status"])
        self.status_bar.showMessage("就绪 | 未连接串口", 0)

    def _build_serial_config_widget(self) -> QGroupBox:
        group = QGroupBox("串口配置 | Serial Configuration")
        group.setFont(FONT_CONFIG["title"])
        layout = QGridLayout(group)
        # 间距适配（原25 → 15，原15 → 10）
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(5)

        layout.addWidget(QLabel("串口 Port："), 0, 0, Qt.AlignRight | Qt.AlignVCenter)
        self.serial_combo = QComboBox()
        # 串口选择框宽度适配（原300 → 200）
        self.serial_combo.setMinimumWidth(150)
        self.serial_combo.setFont(FONT_CONFIG["mono"])
        # 设置拉伸策略，最大化时自动加宽
        self.serial_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.serial_combo, 0, 1)

        layout.addWidget(QLabel("波特率 Baud："), 0, 2, Qt.AlignRight | Qt.AlignVCenter)
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200", "230400", "460800"])
        self.baudrate_combo.setCurrentText("9600")
        self.baudrate_combo.setMinimumWidth(50)  # 原150 → 100
        layout.addWidget(self.baudrate_combo, 0, 3)

        layout.addWidget(QLabel("数据位 Data："), 1, 0, Qt.AlignRight | Qt.AlignVCenter)
        self.databits_combo = QComboBox()
        self.databits_combo.addItems(["5", "6", "7", "8"])
        self.databits_combo.setCurrentText("8")
        self.databits_combo.setMinimumWidth(50)  # 原150 → 100
        layout.addWidget(self.databits_combo, 1, 1)

        layout.addWidget(QLabel("停止位 Stop："), 1, 2, Qt.AlignRight | Qt.AlignVCenter)
        self.stopbits_combo = QComboBox()
        self.stopbits_combo.addItems(["1", "1.5", "2"])
        self.stopbits_combo.setCurrentText("1")
        self.stopbits_combo.setMinimumWidth(50)  # 原150 → 100
        layout.addWidget(self.stopbits_combo, 1, 3)

        layout.addWidget(QLabel("校验位 Parity："), 2, 0, Qt.AlignRight | Qt.AlignVCenter)
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(["无 None", "奇校验 Odd", "偶校验 Even"])
        self.parity_combo.setCurrentText("无 None")
        self.parity_combo.setMinimumWidth(50)  # 原150 → 100
        layout.addWidget(self.parity_combo, 2, 1)

        layout.addWidget(QLabel("流控 Flow："), 2, 2, Qt.AlignRight | Qt.AlignVCenter)
        self.rts_cts_check = QCheckBox("RTS/CTS")
        self.rts_cts_check.setMinimumHeight(20)  # 原30 → 20
        layout.addWidget(self.rts_cts_check, 2, 3)

        self.open_close_btn = QPushButton("打开串口 Open")
        self.open_close_btn.setObjectName("primaryBtn")
        self.open_close_btn.setMinimumWidth(50)  # 原150 → 100
        self.open_close_btn.setMinimumHeight(25)  # 原45 → 35
        self.open_close_btn.clicked.connect(self.toggle_serial)
        layout.addWidget(self.open_close_btn, 0, 4, 3, 1)

        return group

    def _build_modbus_config_widget(self) -> QGroupBox:
        group = QGroupBox("Modbus 配置 | RTU Master（01/02/03/04/05/06/15/16）")
        group.setFont(FONT_CONFIG["title"])
        layout = QGridLayout(group)
        # 间距适配（原25 → 15，原18 → 10）
        layout.setHorizontalSpacing(15)
        layout.setVerticalSpacing(10)

        self.modbus_status_label = QLabel("Disconnected")
        self.modbus_status_label.setStyleSheet("color: #E74C3C; font-weight: bold; font-size: 6px;")  # 原14 → 12
        layout.addWidget(self.modbus_status_label, 0, 0, 1, 2)

        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setSpacing(15)  # 原30 → 15

        self.tx_label = QLabel("Tx = 0")
        self.tx_label.setStyleSheet("color: #2980B9; font-weight: bold;")
        self.err_label = QLabel("Err = 0")
        self.err_label.setStyleSheet("color: #E74C3C; font-weight: bold;")
        self.id_label = QLabel("ID = 1")
        self.f_label = QLabel("F = 03")
        self.sr_label = QLabel("SR = 1000ms")

        for lbl in [self.tx_label, self.err_label, self.id_label, self.f_label, self.sr_label]:
            lbl.setFont(FONT_CONFIG["mono"])
            lbl.setMinimumHeight(10)  # 原30 → 15
            status_layout.addWidget(lbl)
        status_layout.addStretch()

        layout.addWidget(status_widget, 0, 2, 1, 8)

        layout.addWidget(QLabel("从站地址 ID："), 1, 0, Qt.AlignRight)
        self.slave_id_edit = QLineEdit("1")
        self.slave_id_edit.setMinimumWidth(50)  # 原120 → 100
        self.slave_id_edit.setMinimumHeight(10)  # 原35 → 20
        self.slave_id_edit.setFont(FONT_CONFIG["mono"])
        self.slave_id_edit.editingFinished.connect(lambda: self._update_modbus_status("id"))
        layout.addWidget(self.slave_id_edit, 1, 1)

        layout.addWidget(QLabel("功能码 Func："), 1, 2, Qt.AlignRight)
        self.func_code_combo = QComboBox()
        self.func_code_combo.setMinimumWidth(100)  # 原280 → 200
        # 设置拉伸策略
        self.func_code_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        for code, (name, _, desc, _) in FUNC_CODE_MAP.items():
            self.func_code_combo.addItem(f"{code:02d} {name} ({desc})", code)
        self.func_code_combo.currentIndexChanged.connect(self._on_func_code_changed)
        layout.addWidget(self.func_code_combo, 1, 3)

        layout.addWidget(QLabel("起始地址 Addr："), 1, 4, Qt.AlignRight)
        self.start_addr_edit = QLineEdit("0")
        self.start_addr_edit.setMinimumWidth(50)  # 原120 → 100
        self.start_addr_edit.setMinimumHeight(10)  # 原35 → 20
        self.start_addr_edit.setFont(FONT_CONFIG["mono"])
        self.start_addr_edit.editingFinished.connect(lambda: self._validate_addr_input())
        layout.addWidget(self.start_addr_edit, 1, 5)

        layout.addWidget(QLabel("数量 Qty："), 1, 6, Qt.AlignRight)
        self.count_edit = QLineEdit("10")
        self.count_edit.setMinimumWidth(50)  # 原120 → 100
        self.count_edit.setMinimumHeight(10)  # 原35 → 20
        self.count_edit.setFont(FONT_CONFIG["mono"])
        self.count_edit.editingFinished.connect(self._adjust_table_rows)
        layout.addWidget(self.count_edit, 1, 7)

        layout.addWidget(QLabel("扫描周期 MS："), 2, 0, Qt.AlignRight)
        self.interval_edit = QLineEdit("1000")
        self.interval_edit.setMinimumWidth(100)  # 原120 → 100
        self.interval_edit.setMinimumHeight(20)  # 原35 → 20
        self.interval_edit.setFont(FONT_CONFIG["mono"])
        self.interval_edit.editingFinished.connect(lambda: self._update_modbus_status("interval"))
        layout.addWidget(self.interval_edit, 2, 1)

        layout.addWidget(QLabel("写操作值 Value："), 2, 2, Qt.AlignRight)
        self.write_value_edit = QLineEdit()
        self.write_value_edit.setMinimumWidth(150)  # 原280 → 220
        self.write_value_edit.setMinimumHeight(10)  # 原35 → 20
        self.write_value_edit.setFont(FONT_CONFIG["mono"])
        self.write_value_edit.setPlaceholderText("线圈：0/1/True/False | 寄存器：0-65535 | 多值用逗号分隔")
        self.write_value_edit.setEnabled(False)
        # 设置拉伸策略
        self.write_value_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.write_value_edit, 2, 3, 1, 3)

        layout.addWidget(QLabel("显示模式："), 2, 6, Qt.AlignRight)
        self.display_mode_combo = QComboBox()
        self.display_mode_combo.setMinimumWidth(50)  # 原120 → 80
        self.display_mode_combo.addItems(DISPLAY_MODE_MAP.keys())
        self.display_mode_combo.currentTextChanged.connect(self._on_display_mode_changed)
        layout.addWidget(self.display_mode_combo, 2, 7)

        self.modbus_btn = QPushButton("开始轮询 Start Poll")
        self.modbus_btn.setObjectName("primaryBtn")
        self.modbus_btn.setMinimumWidth(50)  # 原160 → 120
        self.modbus_btn.setMinimumHeight(10)  # 原45 → 40
        self.modbus_btn.clicked.connect(self.toggle_modbus_operation)
        self.modbus_btn.setEnabled(False)
        layout.addWidget(self.modbus_btn, 3, 0, 1, 2)

        self.clear_modbus_btn = QPushButton("清空数据 Clear")
        self.clear_modbus_btn.setMinimumWidth(120)  # 原160 → 120
        self.clear_modbus_btn.setMinimumHeight(20)  # 原40 → 35
        self.clear_modbus_btn.clicked.connect(self.clear_modbus_table)
        layout.addWidget(self.clear_modbus_btn, 3, 2, 1, 2)

        self.clear_modbus_log_btn = QPushButton("清空日志 Clear Log")
        self.clear_modbus_log_btn.setMinimumWidth(50)  # 原160 → 120
        self.clear_modbus_log_btn.setMinimumHeight(10)  # 原40 → 35
        self.clear_modbus_log_btn.clicked.connect(self.clear_receive)
        layout.addWidget(self.clear_modbus_log_btn, 3, 4, 1, 2)

        self.manual_write_btn = QPushButton("执行写操作 Write")
        self.manual_write_btn.setObjectName("primaryBtn")
        self.manual_write_btn.setMinimumWidth(50)  # 原160 → 120
        self.manual_write_btn.setMinimumHeight(10)  # 原45 → 40
        self.manual_write_btn.clicked.connect(self.execute_manual_write)
        self.manual_write_btn.setEnabled(False)
        layout.addWidget(self.manual_write_btn, 3, 6, 1, 2)

        # 表格适配：移除固定宽度，改为自适应
        self.modbus_table = QTableWidget()
        self.modbus_table.setColumnCount(2)
        self.modbus_table.setHorizontalHeaderLabels(["Address (Dec)", "Value"])
        # 列宽自适应：Address列根据内容调整，Value列拉伸
        self.modbus_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.modbus_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.modbus_table.setRowCount(10)
        self.modbus_table.setAlternatingRowColors(True)
        self.modbus_table.setMinimumHeight(100)  # 原500 → 300
        # 设置表格拉伸策略，最大化时自动占满空间
        self.modbus_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._init_modbus_table()
        layout.addWidget(self.modbus_table, 4, 0, 1, 8)

        return group

    def _build_io_widget(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(10)  # 原25 → 20

        receive_group = QGroupBox("接收日志 | Receive Log")
        receive_group.setFont(FONT_CONFIG["title"])
        receive_layout = QVBoxLayout(receive_group)
        # 设置接收区拉伸策略
        receive_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        receive_ctrl = QHBoxLayout()
        self.hex_receive_check = QCheckBox("十六进制显示 Hex")
        self.timestamp_check = QCheckBox("显示时间戳 Time")
        self.timestamp_check.setChecked(True)
        self.auto_wrap_check = QCheckBox("自动换行 Wrap")
        self.auto_wrap_check.setChecked(True)
        self.auto_scroll_check = QCheckBox("自动滚屏 Scroll")
        self.auto_scroll_check.setChecked(True)

        self.log_filter_combo = QComboBox()
        self.log_filter_combo.addItems(["全部日志", "仅Modbus", "仅串口"])
        self.log_filter_combo.setMinimumWidth(80)  # 原150 → 120
        self.log_filter_combo.currentTextChanged.connect(self._filter_receive_log)

        for cb in [self.hex_receive_check, self.timestamp_check, self.auto_wrap_check, self.auto_scroll_check]:
            cb.setMinimumHeight(20)  # 原30 → 25

        receive_ctrl.addWidget(self.hex_receive_check)
        receive_ctrl.addWidget(self.timestamp_check)
        receive_ctrl.addWidget(self.auto_wrap_check)
        receive_ctrl.addWidget(self.auto_scroll_check)
        receive_ctrl.addWidget(QLabel("日志过滤："))
        receive_ctrl.addWidget(self.log_filter_combo)
        receive_ctrl.addStretch()

        self.copy_receive_btn = QPushButton("复制 Copy")
        self.copy_receive_btn.setMinimumWidth(80)  # 原100 → 80
        self.copy_receive_btn.setMinimumHeight(20)  # 原40 → 35
        self.copy_receive_btn.clicked.connect(self.copy_receive_content)

        self.save_log_btn = QPushButton("保存 Save")
        self.save_log_btn.setMinimumWidth(80)  # 原100 → 80
        self.save_log_btn.setMinimumHeight(20)  # 原40 → 35
        self.save_log_btn.clicked.connect(self.save_receive_log)

        self.clear_receive_btn = QPushButton("清空 Clear")
        self.clear_receive_btn.setMinimumWidth(80)  # 原100 → 80
        self.clear_receive_btn.setMinimumHeight(20)  # 原40 → 35
        self.clear_receive_btn.clicked.connect(self.clear_receive)

        receive_ctrl.addWidget(self.copy_receive_btn)
        receive_ctrl.addWidget(self.save_log_btn)
        receive_ctrl.addWidget(self.clear_receive_btn)
        receive_layout.addLayout(receive_ctrl)

        self.receive_text = QTextEdit()
        self.receive_text.setReadOnly(True)
        self.receive_text.setFont(FONT_CONFIG["mono"])
        self.receive_text.setLineWrapMode(
            QTextEdit.WidgetWidth if self.auto_wrap_check.isChecked() else QTextEdit.NoWrap)
        self.receive_text.setMinimumHeight(100)  # 原400 → 250
        # 设置接收框拉伸策略
        self.receive_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.auto_wrap_check.clicked.connect(self._toggle_auto_wrap)
        receive_layout.addWidget(self.receive_text)

        self.byte_count_label = QLabel("总接收字节：0 | 本次会话：0")
        self.byte_count_label.setAlignment(Qt.AlignRight)
        self.byte_count_label.setFont(FONT_CONFIG["mono"])
        self.byte_count_label.setMinimumHeight(10)  # 原30 → 25
        receive_layout.addWidget(self.byte_count_label)

        send_group = QGroupBox("发送数据 | Transmit Data")
        send_group.setFont(FONT_CONFIG["title"])
        send_layout = QVBoxLayout(send_group)
        # 设置发送区拉伸策略（宽度占比降低）
        send_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        send_ctrl = QHBoxLayout()
        self.hex_send_check = QCheckBox("十六进制发送 Hex")
        self.auto_clear_send_check = QCheckBox("发送后清空 Clear After Send")
        self.add_newline_check = QCheckBox("自动加换行 Newline")
        self.auto_crc_check = QCheckBox("自动计算Modbus CRC")
        self.auto_crc_check.setChecked(True)

        for cb in [self.hex_send_check, self.auto_clear_send_check, self.add_newline_check, self.auto_crc_check]:
            cb.setMinimumHeight(10)  # 原30 → 25

        send_ctrl.addWidget(self.hex_send_check)
        send_ctrl.addWidget(self.auto_clear_send_check)
        send_ctrl.addWidget(self.add_newline_check)
        send_ctrl.addWidget(self.auto_crc_check)
        send_ctrl.addStretch()

        self.loop_send_check = QCheckBox("循环发送 Loop")
        self.loop_send_check.setMinimumHeight(15)  # 原30 → 25
        self.loop_interval_edit = QLineEdit("1000")
        self.loop_interval_edit.setMinimumWidth(50)  # 原100 → 80
        self.loop_interval_edit.setMinimumHeight(10)  # 原35 → 30
        self.loop_interval_edit.setPlaceholderText("间隔(ms)")
        self.loop_interval_edit.setFont(FONT_CONFIG["mono"])
        self.loop_interval_edit.setEnabled(False)
        self.loop_send_check.clicked.connect(
            lambda: self.loop_interval_edit.setEnabled(self.loop_send_check.isChecked()))
        send_ctrl.addWidget(self.loop_send_check)
        send_ctrl.addWidget(QLabel("间隔："))
        send_ctrl.addWidget(self.loop_interval_edit)
        send_layout.addLayout(send_ctrl)

        self.send_text = QTextEdit()
        self.send_text.setFont(FONT_CONFIG["mono"])
        self.send_text.setMinimumHeight(50)  # 原150 → 100
        # 设置发送框拉伸策略
        self.send_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        send_layout.addWidget(self.send_text)

        send_btn_layout = QHBoxLayout()
        self.send_btn = QPushButton("发送 Send")
        self.send_btn.setObjectName("primaryBtn")
        self.send_btn.setMinimumWidth(50)  # 原120 → 100
        self.send_btn.setMinimumHeight(10)  # 原45 → 40
        self.send_btn.clicked.connect(self.send_data)
        self.send_btn.setEnabled(False)

        self.stop_loop_btn = QPushButton("停止循环 Stop")
        self.stop_loop_btn.setMinimumWidth(50)  # 原120 → 100
        self.stop_loop_btn.setMinimumHeight(10)  # 原40 → 35
        self.stop_loop_btn.clicked.connect(self.stop_loop_send)
        self.stop_loop_btn.setEnabled(False)

        send_btn_layout.addWidget(self.send_btn)
        send_btn_layout.addWidget(self.stop_loop_btn)
        send_btn_layout.addStretch()
        send_layout.addLayout(send_btn_layout)

        # 调整收发区拉伸权重（原3:1 → 7:1，更合理）
        layout.addWidget(receive_group, stretch=7)
        layout.addWidget(send_group, stretch=1)

        return widget

    # ===================== UI 辅助方法 =====================
    def _init_modbus_table(self) -> None:
        for i in range(self.modbus_table.rowCount()):
            addr_item = QTableWidgetItem(f"{i:05d}")
            addr_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            addr_item.setBackground(QColor(248, 248, 248))
            addr_item.setFont(FONT_CONFIG["mono"])
            self.modbus_table.setItem(i, 0, addr_item)

            val_item = QTableWidgetItem("0")
            val_item.setFont(FONT_CONFIG["mono"])
            self.modbus_table.setItem(i, 1, val_item)

        # 行高适配（原35 → 10）
        for i in range(self.modbus_table.rowCount()):
            self.modbus_table.setRowHeight(i, 10)

    def _adjust_table_rows(self) -> None:
        count = validate_numeric_input(self.count_edit.text(), 1, 1000, "数量")
        if count:
            self.modbus_table.setRowCount(count)
            for i in range(self.modbus_table.rowCount()):
                self.modbus_table.setRowHeight(i, 10)
            self._init_modbus_table()

    def _on_func_code_changed(self) -> None:
        func_code = self.func_code_combo.currentData()
        is_write = FUNC_CODE_MAP[func_code][1] == "write"

        self.write_value_edit.setEnabled(is_write)
        self.manual_write_btn.setEnabled(is_write and self.is_serial_open)
        self.interval_edit.setEnabled(not is_write)

        self.f_label.setText(f"F = {func_code:02d}")
        if is_write:
            self.modbus_btn.setText("写操作需点击「执行写操作」")
            self.modbus_btn.setEnabled(False)
            if func_code in [5, 15]:
                self.write_value_edit.setPlaceholderText("线圈值：0/1/True/False | 多值用逗号分隔")
            else:
                self.write_value_edit.setPlaceholderText("寄存器值：0-65535 | 多值用逗号分隔")
        else:
            self.modbus_btn.setText("开始轮询 Start Poll")
            self.modbus_btn.setEnabled(self.is_serial_open)
            self.write_value_edit.setPlaceholderText("写操作值 Value：线圈：0/1，寄存器：十进制，多值用逗号分隔")

        self._validate_addr_input()

    def _validate_addr_input(self) -> None:
        func_code = self.func_code_combo.currentData()
        addr = validate_numeric_input(self.start_addr_edit.text(), 0, 65535, "起始地址")
        if addr and not validate_modbus_addr(func_code, addr):
            self.start_addr_edit.setText(str(FUNC_CODE_MAP[func_code][3][0]))

    def _on_display_mode_changed(self, text: str) -> None:
        self.display_mode = DISPLAY_MODE_MAP[text]
        for row in range(self.modbus_table.rowCount()):
            val_item = self.modbus_table.item(row, 1)
            if val_item:
                try:
                    raw_text = val_item.text().replace("0x", "").replace("0b", "").strip()
                    if raw_text in ["0", "1"]:
                        raw_val = int(raw_text)
                    else:
                        raw_val = int(raw_text, 0)
                    val_item.setText(format_value(raw_val, self.display_mode))
                except:
                    pass

    def _toggle_auto_wrap(self) -> None:
        mode = QTextEdit.WidgetWidth if self.auto_wrap_check.isChecked() else QTextEdit.NoWrap
        self.receive_text.setLineWrapMode(mode)

    def _update_modbus_status(self, type_: str) -> None:
        if type_ == "id":
            slave_id = validate_numeric_input(self.slave_id_edit.text(), 1, 247, "从站地址")
            if slave_id:
                self.id_label.setText(f"ID = {slave_id}")
        elif type_ == "interval":
            interval = validate_numeric_input(self.interval_edit.text(), 10, 30000, "扫描周期")
            if interval:
                self.sr_label.setText(f"SR = {interval}ms")

    def _filter_receive_log(self, filter_type: str) -> None:
        original_text = self.receive_text.toPlainText()
        lines = original_text.split("\n")
        filtered_lines = []

        for line in lines:
            if not line.strip():
                continue
            if filter_type == "全部日志":
                filtered_lines.append(line)
            elif filter_type == "仅Modbus" and "[Modbus-" in line:
                filtered_lines.append(line)
            elif filter_type == "仅串口" and "[串口-" in line:
                filtered_lines.append(line)

        self.receive_text.clear()
        self.receive_text.setText("\n".join(filtered_lines))

    # ===================== 串口操作 =====================
    def scan_serial_ports(self) -> None:
        current_port = self.serial_combo.currentText()
        valid_ports = scan_valid_ports()

        current_ports = [self.serial_combo.itemText(i) for i in range(self.serial_combo.count())]
        if valid_ports != current_ports:
            self.serial_combo.clear()
            self.serial_combo.addItems(valid_ports)
            if current_port and current_port in valid_ports:
                self.serial_combo.setCurrentText(current_port)

    def toggle_serial(self) -> None:
        if not self.is_serial_open:
            try:
                if not self.serial_combo.currentText():
                    QMessageBox.warning(self, "串口错误", "请选择有效的串口")
                    return
                port = self.serial_combo.currentText().split(" - ")[0]
                self.serial.port = port
                self.serial.baudrate = int(self.baudrate_combo.currentText())
                self.serial.bytesize = int(self.databits_combo.currentText())
                self.serial.stopbits = float(self.stopbits_combo.currentText())
                self.serial.parity = {
                    "无 None": serial.PARITY_NONE,
                    "奇校验 Odd": serial.PARITY_ODD,
                    "偶校验 Even": serial.PARITY_EVEN
                }[self.parity_combo.currentText()]
                self.serial.timeout = 0.1
                self.serial.rtscts = self.rts_cts_check.isChecked()
                self.serial.xonxoff = False
                self.serial.dsrdtr = False

                self.serial.open()
                self.is_serial_open = True
                self.open_close_btn.setText("关闭串口 Close")
                self.send_btn.setEnabled(True)

                func_code = self.func_code_combo.currentData()
                self.modbus_btn.setEnabled(FUNC_CODE_MAP[func_code][1] == "read")
                self.manual_write_btn.setEnabled(FUNC_CODE_MAP[func_code][1] == "write")

                self.modbus_status_label.setText("Connected")
                self.modbus_status_label.setStyleSheet("color: #27AE60; font-weight: bold; font-size: 12px;")
                self.status_bar.showMessage(f"串口已打开：{port} | 波特率：{self.serial.baudrate}", 3000)

                self.receive_thread = SerialReceiveThread(self.serial)
                self.receive_thread.receive_signal.connect(self.handle_receive_data)
                self.receive_thread.error_signal.connect(lambda msg: self.status_bar.showMessage(msg, 3000))
                self.receive_thread.start()
                self.session_receive_bytes = 0
            except Exception as e:
                QMessageBox.critical(self, "串口错误", f"打开串口失败：{str(e)}\n请检查串口是否被占用")
        else:
            self.stop_all_operations()
            self.serial.close()
            self.is_serial_open = False
            self.open_close_btn.setText("打开串口 Open")
            self.send_btn.setEnabled(False)
            self.modbus_btn.setEnabled(False)
            self.manual_write_btn.setEnabled(False)
            self.modbus_status_label.setText("Disconnected")
            self.modbus_status_label.setStyleSheet("color: #E74C3C; font-weight: bold; font-size: 12px;")
            self.status_bar.showMessage("串口已关闭", 3000)

    # ===================== 数据收发 =====================
    def handle_receive_data(self, data: bytes) -> None:
        self.total_receive_bytes += len(data)
        self.session_receive_bytes += len(data)
        self.byte_count_label.setText(f"总接收字节：{self.total_receive_bytes} | 本次会话：{self.session_receive_bytes}")

        timestamp = QDateTime.currentDateTime().toString(
            "yyyy-MM-dd hh:mm:ss.zzz") if self.timestamp_check.isChecked() else ""
        if self.hex_receive_check.isChecked():
            display_data = data.hex(' ')
        else:
            try:
                display_data = data.decode('utf-8', errors='replace')
            except:
                display_data = str(data)

        log_prefix = f"[串口-接收][{timestamp}] " if timestamp else "[串口-接收] "
        log_line = f"{log_prefix}{display_data}\n"
        self.receive_text.append(log_line)

        if self.auto_scroll_check.isChecked():
            self.receive_text.moveCursor(self.receive_text.textCursor().End)

    def send_data(self) -> None:
        if not self.is_serial_open:
            QMessageBox.warning(self, "错误", "串口未打开")
            return
        try:
            send_text = self.send_text.toPlainText().strip()
            if not send_text:
                return

            if self.hex_send_check.isChecked():
                send_hex = send_text.replace(" ", "").replace("\n", "").replace("\r", "")
                if len(send_hex) % 2 != 0:
                    raise Exception("十六进制数据长度必须为偶数")

                send_data = bytes.fromhex(send_hex)

                if self.auto_crc_check.isChecked() and len(send_data) >= 2:
                    if len(send_data) >= 4 and send_data[-2:] == modbus_crc16(send_data[:-2]):
                        send_data = send_data[:-2]
                    send_data += modbus_crc16(send_data)
                    self.status_bar.showMessage(f"自动计算CRC：{send_data[-2:].hex()}", 2000)
            else:
                send_data = send_text.encode('utf-8')
                if self.add_newline_check.isChecked():
                    send_data += b'\r\n'

            self.serial.write(send_data)
            self.status_bar.showMessage(f"发送成功：{len(send_data)} 字节", 2000)

            timestamp = QDateTime.currentDateTime().toString(
                "yyyy-MM-dd hh:mm:ss.zzz") if self.timestamp_check.isChecked() else ""
            log_prefix = f"[串口-发送][{timestamp}] " if timestamp else "[串口-发送] "

            if self.hex_receive_check.isChecked():
                log_data = send_data.hex(' ')
            else:
                log_data = send_data.decode('utf-8', errors='replace')

            self.receive_text.append(f"{log_prefix}{log_data}\n")

            if self.auto_clear_send_check.isChecked():
                self.send_text.clear()

            if self.loop_send_check.isChecked() and not self.is_loop_sending:
                interval = validate_numeric_input(self.loop_interval_edit.text(), 10, 30000, "循环间隔") or 1000
                self.loop_send_timer.start(interval)
                self.is_loop_sending = True
                self.send_btn.setEnabled(False)
                self.stop_loop_btn.setEnabled(True)
                self.status_bar.showMessage(f"开始循环发送（间隔{interval}ms）", 2000)
        except Exception as e:
            err_msg = f"发送失败：{str(e)}"
            self.status_bar.showMessage(err_msg, 2000)
            QMessageBox.critical(self, "错误", err_msg)

    def stop_loop_send(self) -> None:
        self.loop_send_timer.stop()
        self.is_loop_sending = False
        self.send_btn.setEnabled(True)
        self.stop_loop_btn.setEnabled(False)
        self.status_bar.showMessage("循环发送已停止", 2000)

    # ===================== Modbus 操作 =====================
    def toggle_modbus_operation(self) -> None:
        if not self.modbus_thread or not self.modbus_thread.isRunning():
            slave_id = validate_numeric_input(self.slave_id_edit.text(), 1, 247, "从站地址")
            func_code = self.func_code_combo.currentData()
            start_addr = validate_numeric_input(self.start_addr_edit.text(), 0, 65535, "起始地址")
            count = validate_numeric_input(self.count_edit.text(), 1, 1000, "数量")
            interval = validate_numeric_input(self.interval_edit.text(), 10, 30000, "扫描周期")

            if not all([slave_id, func_code, start_addr, count, interval]):
                return

            if not validate_modbus_addr(func_code, start_addr):
                return

            self.modbus_thread = ModbusThread(self.serial)
            self.modbus_thread.set_read_params(slave_id, func_code, start_addr, count, interval)
            self.modbus_thread.poll_result.connect(self.update_modbus_table)
            self.modbus_thread.status_update.connect(lambda msg: self.status_bar.showMessage(msg, 2000))
            self.modbus_thread.log_update.connect(self._append_modbus_log)
            self.modbus_thread.start()
            self.modbus_btn.setText("停止轮询 Stop Poll")
            self.status_bar.showMessage(f"开始Modbus轮询 | 从站{slave_id} 功能码{func_code:02d}", 2000)
        else:
            self.stop_modbus_operation()
            self.modbus_btn.setText("开始轮询 Start Poll")
            self.status_bar.showMessage("Modbus轮询已停止", 2000)

    def stop_modbus_operation(self) -> None:
        if self.modbus_thread and self.modbus_thread.isRunning():
            self.modbus_thread.stop()
            self.modbus_thread.wait()

    def update_modbus_table(self, data_list: List[Union[int, bool]], tx_count: int, err_count: int) -> None:
        self.tx_label.setText(f"Tx = {tx_count}")
        self.err_label.setText(f"Err = {err_count}")

        for row in range(self.modbus_table.rowCount()):
            if row < len(data_list):
                val = data_list[row]
                formatted_val = format_value(val, self.display_mode)
                val_item = QTableWidgetItem(formatted_val)
                val_item.setFont(FONT_CONFIG["mono"])
                self.modbus_table.setItem(row, 1, val_item)
            else:
                val_item = QTableWidgetItem("0")
                val_item.setFont(FONT_CONFIG["mono"])
                self.modbus_table.setItem(row, 1, val_item)

    def _append_modbus_log(self, log_type: str, content: str) -> None:
        timestamp = QDateTime.currentDateTime().toString(
            "yyyy-MM-dd hh:mm:ss.zzz") if self.timestamp_check.isChecked() else ""
        log_prefix = f"[{log_type}][{timestamp}] " if timestamp else f"[{log_type}] "
        self.receive_text.append(f"{log_prefix}{content}\n")

        if self.auto_scroll_check.isChecked():
            self.receive_text.moveCursor(self.receive_text.textCursor().End)

    def execute_manual_write(self) -> None:
        if not self.is_serial_open:
            QMessageBox.warning(self, "错误", "串口未打开")
            return

        slave_id = validate_numeric_input(self.slave_id_edit.text(), 1, 247, "从站地址")
        func_code = self.func_code_combo.currentData()
        start_addr = validate_numeric_input(self.start_addr_edit.text(), 0, 65535, "起始地址")
        count = validate_numeric_input(self.count_edit.text(), 1, 1000, "数量")

        if not all([slave_id, func_code, start_addr, count]):
            return

        if not validate_modbus_addr(func_code, start_addr):
            return

        write_values = parse_write_values(self.write_value_edit.text(), func_code, count)
        if not write_values:
            return

        self.modbus_thread = ModbusThread(self.serial)
        self.modbus_thread.set_write_params(slave_id, func_code, start_addr, count, write_values)
        self.modbus_thread.write_result.connect(self.handle_write_result)
        self.modbus_thread.status_update.connect(lambda msg: self.status_bar.showMessage(msg, 2000))
        self.modbus_thread.log_update.connect(self._append_modbus_log)
        self.modbus_thread.start()

    def handle_write_result(self, success: bool, msg: str) -> None:
        if success:
            QMessageBox.information(self, "操作成功", msg)
        else:
            QMessageBox.critical(self, "操作失败", msg)

    def clear_modbus_table(self) -> None:
        for row in range(self.modbus_table.rowCount()):
            val_item = QTableWidgetItem("0")
            val_item.setFont(FONT_CONFIG["mono"])
            self.modbus_table.setItem(row, 1, val_item)

    def clear_receive(self) -> None:
        self.receive_text.clear()
        self.session_receive_bytes = 0
        self.byte_count_label.setText(f"总接收字节：{self.total_receive_bytes} | 本次会话：0")

    def copy_receive_content(self) -> None:
        clipboard = QApplication.clipboard()
        clipboard.setText(self.receive_text.toPlainText())
        self.status_bar.showMessage("接收日志已复制到剪贴板", 2000)

    def save_receive_log(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(self, "保存日志",
                                                   f"modbus_log_{QDateTime.currentDateTime().toString('yyyyMMddhhmmss')}.txt",
                                                   "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.receive_text.toPlainText())
                self.status_bar.showMessage(f"日志已保存到：{file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"日志保存失败：{str(e)}")

    def stop_all_operations(self) -> None:
        self.stop_loop_send()
        self.stop_modbus_operation()
        if self.receive_thread and self.receive_thread.isRunning():
            self.receive_thread.stop()
            self.receive_thread.wait()


# ===================== 程序入口 =====================
if __name__ == "__main__":
    # 解决高DPI显示问题
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setFont(FONT_CONFIG["default"])

    window = ModbusRTUMainWindow()
    sys.exit(app.exec_())