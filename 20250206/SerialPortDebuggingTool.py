import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog
from threading import Thread, Event
import time
import binascii
from datetime import datetime


class SerialDebugger:
    def __init__(self, master):
        self.master = master
        self.serial_port = None
        self.receive_flag = Event()
        self.auto_send_flag = False
        self.rx_counter = 0
        self.tx_counter = 0
        self.recv_color = '#FF0000'  # 默认接收颜色红色
        self.send_color = '#0000FF'  # 默认发送颜色蓝色
        self.extension_visible = False  # 扩展窗口可见状态

        # 获取默认Checkbutton背景颜色
        temp = tk.Checkbutton(master)
        self.default_bg = temp.cget('bg')
        temp.destroy()

        # 初始化ttk样式
        self.style = ttk.Style()
        self.style.configure('Yellow.TCombobox', fieldbackground='yellow')

        # 初始化界面
        self.setup_ui()
        self.setup_extension_window()
        self.update_ports()

        # 绑定事件
        self.port_combo.bind("<<ComboboxSelected>>", self.on_port_change)

    def setup_ui(self):
        """初始化主界面布局"""
        self.master.geometry("990x700")
        self.master.title("串口调试工具 - 智能模拟传感器答复")
        self.master.minsize(650, 450)

        # 配置主窗口网格布局
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=0, minsize=0)  # 扩展窗口列
        self.master.grid_rowconfigure(0, weight=1)  # 数据显示区
        self.master.grid_rowconfigure(1, weight=0)  # 控制区
        self.master.grid_rowconfigure(2, weight=0)  # 状态栏

        # ========== 数据显示区 ==========
        display_frame = ttk.Frame(self.master)
        display_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.text_display = tk.Text(display_frame, state=tk.DISABLED, wrap=tk.WORD)
        scroll_display = ttk.Scrollbar(display_frame, orient="vertical", command=self.text_display.yview)
        self.text_display.configure(yscrollcommand=scroll_display.set)

        self.text_display.grid(row=0, column=0, sticky="nsew")
        scroll_display.grid(row=0, column=1, sticky="ns")
        display_frame.grid_columnconfigure(0, weight=1)
        display_frame.grid_rowconfigure(0, weight=1)

        # ========== 中间控制区 ==========
        control_frame = ttk.Frame(self.master)
        control_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=2)
        control_frame.grid_columnconfigure(0, minsize=200, weight=0)
        control_frame.grid_columnconfigure(1, weight=1)
        control_frame.grid_columnconfigure(2, minsize=250, weight=0)
        control_frame.grid_rowconfigure(0, minsize=155, weight=0)

        # 串口设置区
        self.setup_serial_controls(control_frame)
        # 发送输入区
        self.setup_send_controls(control_frame)
        # 功能区
        self.setup_function_controls(control_frame)

        # ========== 状态栏 ==========
        self.setup_status_bar()

    def setup_extension_window(self):
        """初始化扩展窗口"""
        self.extension_frame = ttk.Frame(self.master, width=425)
        self.extension_frame.grid(row=0, column=1, sticky="nsew")
        self.extension_frame.grid_remove()

        # 创建Notebook
        self.notebook = ttk.Notebook(self.extension_frame)
        self.notebook.pack(expand=True, fill='both')

        # 预置命令标签页
        self.preset_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.preset_frame, text="预置命令")

        # 自动答复标签页
        self.auto_reply_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.auto_reply_frame, text="自动答复")

        # 设置固定宽度
        self.extension_frame.grid_propagate(False)
        self.extension_frame.config(width=425)

    def toggle_extension(self):
        """切换扩展窗口显示状态"""
        self.extension_visible = not self.extension_visible
        if self.extension_visible:
            self.extension_frame.grid()
            self.master.grid_columnconfigure(1, minsize=425, weight=0)
        else:
            self.extension_frame.grid_remove()
            self.master.grid_columnconfigure(1, weight=0, minsize=0)

    def setup_status_bar(self):
        """初始化底部状态栏"""
        status_bar = ttk.Frame(self.master, height=22)
        status_bar.grid(row=2, column=0, columnspan=2, sticky="sew")

        self.status_conn = ttk.Label(status_bar, text="未连接", anchor=tk.W)
        self.status_rx = ttk.Label(status_bar, text="RX:0", width=8)
        self.status_tx = ttk.Label(status_bar, text="TX:0", width=8)
        self.status_author = ttk.Label(status_bar, text="Power by DeepSeek", anchor=tk.E)

        self.status_conn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.status_rx.pack(side=tk.LEFT, padx=5)
        self.status_tx.pack(side=tk.LEFT, padx=5)
        self.status_author.pack(side=tk.RIGHT)

    def setup_serial_controls(self, parent):
        """串口设置区"""
        frame = ttk.LabelFrame(parent, text="串口设置", padding=5)  # padding 与顶部的距离
        frame.grid(row=0, column=0, sticky="nsew", padx=2)
        frame.grid_propagate(False)
        frame.config(width=200, height=155)

        frame.grid_columnconfigure(1, weight=1)
        row = 0

        ttk.Label(frame, text="端口号:").grid(row=row, column=0, sticky=tk.W)
        self.port_combo = ttk.Combobox(frame)
        self.port_combo.grid(row=row, column=1, sticky=tk.EW, padx=6)
        row += 1

        ttk.Label(frame, text="波特率:").grid(row=row, column=0, sticky=tk.W)
        self.baud_combo = ttk.Combobox(frame, values=[
            '300', '600', '1200', '2400', '4800', '9600',
            '14400', '19200', '38400', '57600', '115200'
        ])
        self.baud_combo.set('9600')
        self.baud_combo.grid(row=row, column=1, sticky=tk.EW, padx=6)
        row += 1

        # 数据位和校验行
        param_row = ttk.Frame(frame)
        param_row.grid(row=row, column=0, columnspan=2, sticky=tk.EW)
        ttk.Label(param_row, text="数据位:").grid(row=0, column=0, padx=1)
        self.data_bits = ttk.Combobox(param_row, values=['5', '6', '7', '8'], width=3)
        self.data_bits.set('8')
        self.data_bits.grid(row=0, column=1, padx=4)
        ttk.Label(param_row, text="校验:").grid(row=0, column=2, padx=1)
        self.parity = ttk.Combobox(param_row, values=['无', '奇校验', '偶校验'], width=3)
        self.parity.set('无')
        self.parity.grid(row=0, column=3, sticky=tk.EW)
        param_row.grid_columnconfigure(3, weight=1)
        row += 1

        # 停止位和流控行
        param_row = ttk.Frame(frame)
        param_row.grid(row=row, column=0, columnspan=2, sticky=tk.EW)
        ttk.Label(param_row, text="停止位:").grid(row=0, column=0, padx=1)
        self.stop_bits = ttk.Combobox(param_row, values=['1', '1.5', '2'], width=3)
        self.stop_bits.set('1')
        self.stop_bits.grid(row=0, column=1, padx=4)
        ttk.Label(param_row, text="流控:").grid(row=0, column=2, padx=1)
        self.flow_control = ttk.Combobox(param_row, values=['无', 'RTS/CTS', 'XON/XOFF'], width=3)
        self.flow_control.set('无')
        self.flow_control.grid(row=0, column=3, sticky=tk.EW)
        param_row.grid_columnconfigure(3, weight=1)
        row += 1

        self.open_btn = ttk.Button(frame, text="打开端口", command=self.toggle_serial)
        self.open_btn.grid(row=row, column=0, columnspan=2, pady=5, sticky=tk.EW)

    def setup_send_controls(self, parent):
        """发送输入区"""
        frame = ttk.LabelFrame(parent, text="发送区", padding=5)
        frame.grid(row=0, column=1, sticky="nsew", padx=2)
        frame.grid_propagate(False)
        frame.config(height=155)

        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        top_row = ttk.Frame(frame)
        top_row.grid(row=0, column=0, sticky="ew", pady=2)
        ttk.Button(top_row, text="文件发送", command=self.send_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_row, text="数据存至文件", command=self.save_data).pack(side=tk.LEFT, padx=2)
        ttk.Label(top_row, text="末尾添加校验:").pack(side=tk.LEFT)
        self.checksum_combo = ttk.Combobox(top_row, values=['None', 'CRC-16', 'XOR'], width=8)
        self.checksum_combo.set('None')
        self.checksum_combo.pack(side=tk.LEFT, padx=2)
        self.checksum_combo.bind("<<ComboboxSelected>>", self.on_checksum_selected)
        self.on_checksum_selected(None)

        text_frame = ttk.Frame(frame)
        text_frame.grid(row=1, column=0, sticky="nsew")

        self.send_text = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 10))
        scroll_send = ttk.Scrollbar(text_frame, orient="vertical", command=self.send_text.yview)
        self.send_text.configure(yscrollcommand=scroll_send.set)

        self.send_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_send.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_function_controls(self, parent):
        """功能区"""
        frame = ttk.LabelFrame(parent, text="功能设置", padding=5)
        frame.grid(row=0, column=2, sticky="nsew", padx=2)
        frame.grid_propagate(False)
        frame.config(width=250, height=155)

        frame.grid_columnconfigure(0, weight=1)

        top_row = ttk.Frame(frame)
        top_row.grid(row=0, column=0, sticky="ew", pady=2)
        self.hex_send = tk.BooleanVar()
        self.hex_send_cb = tk.Checkbutton(top_row, text="Hex发送", variable=self.hex_send)
        self.hex_send_cb.pack(side=tk.LEFT)
        self.hex_send.trace_add('write', lambda *args: self.update_checkbutton_bg(self.hex_send_cb, self.hex_send))
        self.hex_display = tk.BooleanVar()
        self.hex_display_cb = tk.Checkbutton(top_row, text="Hex显示", variable=self.hex_display)
        self.hex_display_cb.pack(side=tk.LEFT, padx=5)
        self.hex_display.trace_add('write',
                                   lambda *args: self.update_checkbutton_bg(self.hex_display_cb, self.hex_display))
        ttk.Button(top_row, text="清空窗口", command=self.clear_display).pack(side=tk.RIGHT)

        middle_row = ttk.Frame(frame)
        middle_row.grid(row=1, column=0, sticky="ew", pady=2)
        self.timestamp = tk.BooleanVar()
        self.timestamp_cb = tk.Checkbutton(middle_row, text="时间戳", variable=self.timestamp)
        self.timestamp_cb.pack(side=tk.LEFT)
        self.timestamp.trace_add('write', lambda *args: self.update_checkbutton_bg(self.timestamp_cb, self.timestamp))
        color_frame = ttk.Frame(middle_row)
        color_frame.pack(side=tk.RIGHT)
        ttk.Label(color_frame, text="收:").pack(side=tk.LEFT)
        self.recv_color_lbl = tk.Label(color_frame, width=2, bg=self.recv_color, relief="solid")
        self.recv_color_lbl.bind("<Button-1>", lambda e: self.choose_color('recv'))
        self.recv_color_lbl.pack(side=tk.LEFT, padx=2)
        ttk.Label(color_frame, text="发:").pack(side=tk.LEFT)
        self.send_color_lbl = tk.Label(color_frame, width=2, bg=self.send_color, relief="solid")
        self.send_color_lbl.bind("<Button-1>", lambda e: self.choose_color('send'))
        self.send_color_lbl.pack(side=tk.LEFT, padx=2)

        auto_frame = ttk.Frame(frame)
        auto_frame.grid(row=2, column=0, sticky="ew", pady=2)
        ttk.Label(auto_frame, text="间隔(ms):").pack(side=tk.LEFT)
        self.interval_var = ttk.Entry(auto_frame, width=8)
        self.interval_var.insert(0, "1000")
        self.interval_var.pack(side=tk.LEFT, padx=2)
        self.auto_send = tk.BooleanVar()
        self.auto_send_cb = tk.Checkbutton(auto_frame, text="自动发送", variable=self.auto_send,
                                           command=self.toggle_auto_send)
        self.auto_send_cb.pack(side=tk.LEFT)
        self.auto_send.trace_add('write', lambda *args: self.update_checkbutton_bg(self.auto_send_cb, self.auto_send))

        # 修改发送按钮并添加扩展按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, sticky="ew", pady=5)
        ttk.Button(button_frame, text="发送", command=self.send_data).pack(side=tk.LEFT, expand=True)
        ttk.Button(button_frame, text="扩展", command=self.toggle_extension).pack(side=tk.RIGHT)

    def choose_color(self, direction):
        """选择颜色"""
        chinese_dir = "接收" if direction == "recv" else "发送"
        color = colorchooser.askcolor(title=f'选择{chinese_dir}颜色')[1]
        if color:
            if direction == 'recv':
                self.recv_color = color
                self.recv_color_lbl.config(bg=color)
            else:
                self.send_color = color
                self.send_color_lbl.config(bg=color)

    def update_checkbutton_bg(self, checkbutton, var):
        """更新复选框背景颜色"""
        checkbutton.config(bg='yellow' if var.get() else self.default_bg)

    def on_checksum_selected(self, event):
        """校验选项变化事件处理"""
        if self.checksum_combo.get() != 'None':
            self.checksum_combo.config(style='Yellow.TCombobox')
        else:
            self.checksum_combo.config(style='TCombobox')

    def send_file(self):
        """发送文件"""
        if not self.serial_port or not self.serial_port.is_open:
            messagebox.showwarning("警告", "请先打开串口")
            return

        file_path = filedialog.askopenfilename()
        if not file_path: return

        try:
            with open(file_path, 'rb') as f:
                data = f.read()

            if self.hex_send.get():
                hex_str = data.hex()
                data = binascii.unhexlify(hex_str)

            data = self.add_checksum(data)
            self.serial_port.write(data)
            self.tx_counter += len(data)
            self.display_data(data, 'send')
            self.update_counters()
        except Exception as e:
            messagebox.showerror("发送文件错误", str(e))

    def save_data(self):
        """保存数据"""
        content = self.text_display.get("1.0", tk.END)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not file_path: return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("保存成功", "数据已保存至文件")
        except Exception as e:
            messagebox.showerror("保存错误", str(e))

    def add_checksum(self, data):
        """添加校验码"""
        checksum_type = self.checksum_combo.get()
        if checksum_type == 'None':
            return data
        elif checksum_type == 'CRC-16':
            crc = self.calculate_crc16(data)
            return data + crc
        elif checksum_type == 'XOR':
            xor = self.calculate_xor(data)
            return data + xor.to_bytes(1, 'big')
        return data

    def calculate_crc16(self, data):
        """计算CRC16校验"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc.to_bytes(2, 'little')

    def calculate_xor(self, data):
        """计算异或校验"""
        xor = 0
        for byte in data:
            xor ^= byte
        return xor

    def update_ports(self):
        """更新端口列表"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        self.port_combo.set(ports[0] if ports else '')

    def update_status(self, status, success=True):
        """更新状态栏"""
        if success:
            conn_info = f"{self.port_combo.get()} | {self.baud_combo.get()}波特 | {self.data_bits.get()}数据位 | "
            conn_info += f"{self.stop_bits.get()}停止位 | {self.parity.get()} | {self.flow_control.get()}"
            self.status_conn.config(text=conn_info, foreground='green')
        else:
            self.status_conn.config(text=status, foreground='red')

    def update_counters(self):
        """更新计数器"""
        self.status_rx.config(text=f"RX:{self.rx_counter}")
        self.status_tx.config(text=f"TX:{self.tx_counter}")

    def clear_display(self):
        """清空显示"""
        self.text_display.config(state=tk.NORMAL)
        self.text_display.delete(1.0, tk.END)
        self.text_display.config(state=tk.DISABLED)
        self.rx_counter = self.tx_counter = 0
        self.update_counters()

    def toggle_auto_send(self):
        """切换自动发送"""
        self.auto_send_flag = self.auto_send.get()
        if self.auto_send_flag:
            self.auto_send_loop()

    def auto_send_loop(self):
        """自动发送循环"""
        if self.auto_send_flag and self.serial_port.is_open:
            self.send_data()
            self.master.after(max(100, int(self.interval_var.get())), self.auto_send_loop)

    def on_port_change(self, event):
        """端口变更处理"""
        if self.serial_port and self.serial_port.is_open:
            self.close_serial()
            self.open_serial()

    def toggle_serial(self):
        """切换串口状态"""
        if self.serial_port and self.serial_port.is_open:
            self.close_serial()
        else:
            self.open_serial()

    def open_serial(self):
        """打开串口"""
        try:
            params = {
                'port': self.port_combo.get(),
                'baudrate': int(self.baud_combo.get()),
                'bytesize': int(self.data_bits.get()),
                'stopbits': {'1': 1, '1.5': 1.5, '2': 2}[self.stop_bits.get()],
                'parity': {'无': 'N', '奇校验': 'O', '偶校验': 'E'}[self.parity.get()],
                'xonxoff': 1 if self.flow_control.get() == 'XON/XOFF' else 0,
                'rtscts': 1 if self.flow_control.get() == 'RTS/CTS' else 0
            }
            self.serial_port = serial.Serial(**params)
            self.open_btn.config(text="关闭端口")
            self.update_status("", True)
            self.receive_flag.set()
            Thread(target=self.receive_data, daemon=True).start()
        except Exception as e:
            self.update_status(f"连接失败：{str(e)}", False)

    def close_serial(self):
        """关闭串口"""
        self.receive_flag.clear()
        if self.serial_port:
            self.serial_port.close()
        self.open_btn.config(text="打开端口")
        self.status_conn.config(text="未连接", foreground='black')

    def receive_data(self):
        """接收数据"""
        while self.receive_flag.is_set():
            try:
                if self.serial_port.in_waiting:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    self.rx_counter += len(data)
                    self.display_data(data, 'recv')
                    self.update_counters()
                time.sleep(0.01)
            except Exception as e:
                print("接收错误:", e)
                break

    def send_data(self):
        """发送数据"""
        if not (self.serial_port and self.serial_port.is_open):
            messagebox.showwarning("警告", "请先打开串口")
            return

        text = self.send_text.get("1.0", tk.END).strip()
        if not text: return

        try:
            if self.hex_send.get():
                hex_str = text.replace(' ', '').replace('\n', '')
                data = binascii.unhexlify(hex_str)
            else:
                data = text.encode('utf-8')

            data = self.add_checksum(data)
            self.serial_port.write(data)
            self.tx_counter += len(data)
            self.display_data(data, 'send')
            self.update_counters()
        except Exception as e:
            messagebox.showerror("发送错误", str(e))

    def display_data(self, data, direction):
        """显示数据"""
        prefix = "收←◆ " if direction == 'recv' else "发→◇ "
        color = self.send_color if direction == 'send' else self.recv_color

        if self.hex_display.get():
            display = ' '.join(f'{b:02X}' for b in data)
        else:
            try:
                display = data.decode('utf-8', 'replace')
            except:
                display = str(data)

        if self.timestamp.get():
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            full_text = f"[{timestamp}] {prefix}{display}"
        else:
            full_text = f"{prefix}{display}"

        self.text_display.config(state=tk.NORMAL)
        self.text_display.insert(tk.END, full_text + '\n', (color,))
        self.text_display.tag_config(color, foreground=color)
        self.text_display.see(tk.END)
        self.text_display.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = SerialDebugger(root)
    root.mainloop()