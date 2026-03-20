# coding: utf-8
"""
JSON数据生成调度器
用于优化JSON数据文件的生成逻辑，避免频繁写入和死循环问题
"""

import time
import threading
import json
import os
import queue
from datetime import datetime
# 延迟导入logger，避免循环导入
# from logger.logger_config import get_logger

# logger = get_logger(__name__)
logger = None

def _get_logger():
    """延迟获取logger实例"""
    global logger
    if logger is None:
        from logger.logger_config import get_logger
        logger = get_logger(__name__)
    return logger

class JSONScheduler:
    """
    JSON数据生成调度器
    控制JSON数据文件的生成时机和频率，避免频繁写入
    """
    
    def __init__(self, data_dir=None, min_interval=60, max_records=2000, max_pending=1000, batch_size=50):
        """
        初始化调度器
        :param data_dir: 数据目录路径
        :param min_interval: 最小生成间隔（秒），默认60秒
        :param max_records: 最大记录数，超出时清理旧数据
        :param max_pending: 最大待处理数据量，超出时清理旧数据
        :param batch_size: 批量处理数据的大小
        """
        self.data_dir = data_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.min_interval = min_interval
        self.max_records = max_records
        self.max_pending = max_pending
        self.batch_size = batch_size
        self.last_generate_time = 0
        self.is_generating = False
        self.pending_data = []  # 存储待处理的数据
        self.lock = threading.RLock()  # 使用可重入锁，提高并发性能
        self.write_queue = queue.Queue(maxsize=200)  # 增大队列容量，减少阻塞
        self.write_thread_running = True
        self.last_write_time = 0  # 上次写入时间戳
        self.write_error_count = 0  # 写入错误计数
        self.write_success_count = 0  # 写入成功计数
        self.max_retries = 3  # 最大重试次数
        
        # 确保数据目录存在
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)  # 使用exist_ok参数，避免重复创建
            _get_logger().info(f"创建数据目录: {self.data_dir}")
        
        # 启动异步写入线程
        self.write_thread = threading.Thread(target=self._async_write_worker, daemon=True)
        self.write_thread.start()
    
    def should_generate(self):
        """
        判断是否应该生成JSON文件
        :return: bool 是否应该生成
        """
        current_time = time.time()
        time_since_last = current_time - self.last_generate_time
        
        with self.lock:
            pending_count = len(self.pending_data)
        
        # 如果距离上次生成时间超过最小间隔，且当前不在生成过程中
        # 或者待处理数据量超过批量大小
        return (time_since_last >= self.min_interval and not self.is_generating) or \
               (pending_count >= self.batch_size and not self.is_generating)
    
    def add_data(self, price_data, message_data=None):
        """
        添加待处理的数据
        :param price_data: 价格数据
        :param message_data: 消息数据（可选）
        """
        # 快速检查价格数据有效性，避免无效数据进入队列
        if not price_data:
            _get_logger().debug("价格数据为空，跳过添加")
            return
        
        price = price_data.get('price')
        status = price_data.get('status')
        
        # 只添加有效的价格数据或程序启动数据
        if price is None and status != '程序启动':
            _get_logger().debug("价格数据无效且非程序启动状态，跳过添加")
            return
        
        with self.lock:
            # 构建数据对象
            data_entry = {
                'timestamp': int(time.time()),
                'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'price_data': price_data,
                'message_data': message_data
            }
            
            # 添加到待处理队列
            self.pending_data.append(data_entry)
            
            # 如果待处理数据量超过最大值，清理旧数据
            if len(self.pending_data) > self.max_pending:
                # 保留最新的数据
                old_count = len(self.pending_data) - self.max_pending
                self.pending_data = self.pending_data[-self.max_pending:]
                _get_logger().warning(f"待处理数据量超过限制，清理了 {old_count} 条旧数据")
            
            # 定期清理过期数据（每50条数据检查一次）
            if len(self.pending_data) % 50 == 0:
                self._clean_expired_pending_data()
    
    def _clean_expired_pending_data(self):
        """
        清理过期的待处理数据
        """
        current_time = time.time()
        expired_threshold = current_time - 3600  # 1小时前的数据视为过期
        
        # 过滤掉过期数据
        original_count = len(self.pending_data)
        self.pending_data = [data for data in self.pending_data if data.get('timestamp', 0) > expired_threshold]
        cleaned_count = original_count - len(self.pending_data)
        
        if cleaned_count > 0:
            _get_logger().info(f"清理了 {cleaned_count} 条过期的待处理数据")
    
    def generate_json_file(self):
        """
        生成JSON文件（线程安全）
        :return: 文件路径或None
        """
        if not self.should_generate():
            _get_logger().debug("不满足生成条件，跳过JSON文件生成")
            return None
            
        with self.lock:
            if self.is_generating:
                _get_logger().debug("已有生成任务在进行中，跳过本次生成")
                return None
                
            if not self.pending_data:
                _get_logger().debug("没有待处理的数据，跳过生成")
                return None
                
            # 标记为正在生成
            self.is_generating = True
            
            # 复制待处理数据并清空队列，减少锁持有时间
            data_to_process = self.pending_data.copy()
            self.pending_data.clear()
            
        try:
            # 生成文件名
            file_name = datetime.now().strftime('%Y%m%d') + '.json'
            file_path = os.path.join(self.data_dir, file_name)
            
            # 读取现有数据
            existing_data = self._read_existing_data(file_path)
            
            # 合并新数据
            merged_data = self._merge_data(existing_data, data_to_process)
            
            # 添加到异步写入队列，使用非阻塞方式
            try:
                self.write_queue.put((file_path, merged_data), block=False, timeout=0.5)
            except queue.Full:
                _get_logger().warning("写入队列已满，将数据合并到下一批处理")
                with self.lock:
                    # 将数据重新添加到待处理队列
                    self.pending_data.extend(data_to_process)
                return None
            
            # 更新最后生成时间
            self.last_generate_time = time.time()
            _get_logger().info(f"JSON数据已添加到异步写入队列，包含 {len(merged_data)} 条记录")
            return file_path
            
        except Exception as e:
            _get_logger().error(f"生成JSON文件时发生异常: {e}")
            # 发生异常时，将数据重新添加到待处理队列
            try:
                with self.lock:
                    self.pending_data.extend(data_to_process)
            except Exception as e:
                _get_logger().error(f"处理待写入数据时发生异常: {e}")
            return None
        finally:
            # 重置生成状态
            self.is_generating = False
    
    def _async_write_worker(self):
        """
        异步写入工作线程
        """
        while self.write_thread_running:
            try:
                # 从队列中获取写入任务
                try:
                    file_path, data = self.write_queue.get(timeout=0.5)  # 减少超时时间，提高响应速度
                except queue.Empty:
                    # 队列为空时，短暂休眠
                    time.sleep(0.1)
                    continue
                
                # 执行写入
                success = self._write_json_file(file_path, data)
                if success:
                    _get_logger().debug(f"异步写入JSON文件成功: {file_path} (包含 {len(data)} 条记录)")  # 降级为debug日志，减少日志输出
                else:
                    _get_logger().error(f"异步写入JSON文件失败: {file_path}")
                
                # 标记任务完成
                self.write_queue.task_done()
                    
            except Exception as e:
                _get_logger().error(f"异步写入线程发生异常: {e}")
                # 继续运行，不退出线程
                time.sleep(1)
                continue
    
    def _read_existing_data(self, file_path):
        """
        读取现有JSON数据
        :param file_path: 文件路径
        :return: 现有数据列表
        """
        existing_data = []
        
        if not os.path.exists(file_path):
            return existing_data
        
        try:
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size > 10 * 1024 * 1024:  # 增大文件大小限制到10MB
                _get_logger().warning(f"JSON文件过大 ({file_size / (1024*1024):.2f} MB)，将重置文件")
                return existing_data
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', buffering=8192) as f:  # 使用缓冲区，提高读取速度
                content = f.read().strip()
                if content:
                    existing_data = json.loads(content)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
                        
        except (json.JSONDecodeError, ValueError, OSError) as e:
            _get_logger().warning(f"读取现有JSON文件失败: {e}")
            # 尝试修复文件
            try:
                # 重命名损坏的文件
                backup_path = f"{file_path}.backup.{int(time.time())}"
                os.rename(file_path, backup_path)
                _get_logger().info(f"已将损坏的JSON文件备份到: {backup_path}")
            except Exception as e:
                _get_logger().error(f"备份损坏的JSON文件失败: {e}")
            existing_data = []
        
        return existing_data
    
    def _merge_data(self, existing_data, new_data):
        """
        合并现有数据和新数据，去重并限制数量
        :param existing_data: 现有数据
        :param new_data: 新数据
        :return: 合并后的数据
        """
        # 合并数据
        merged_data = existing_data + new_data
        
        # 去重：基于时间戳和价格，优化算法
        unique_dict = {}
        
        for entry in merged_data:
            price_data = entry.get('price_data', {})
            timestamp = entry.get('timestamp', 0)
            price = price_data.get('price')
            status = price_data.get('status')
            
            # 创建唯一键，考虑价格精度问题
            key = f"{timestamp}_{price:.2f}" if isinstance(price, (int, float)) else f"{timestamp}_{price}"
            
            # 特殊处理：保留状态为'程序启动'的初始数据，以及价格不为None的正常数据
            if (price is not None) or (status == '程序启动'):
                # 始终保留最新的数据
                unique_dict[key] = entry
        
        # 转换为列表并按时间戳排序
        unique_data = list(unique_dict.values())
        unique_data.sort(key=lambda x: x.get('timestamp', 0))
        
        # 限制记录数量
        if len(unique_data) > self.max_records:
            # 保留最新的记录
            unique_data = unique_data[-self.max_records:]
            _get_logger().info(f"数据记录数超过限制，保留最新的 {self.max_records} 条记录")
        
        return unique_data
    
    def _write_json_file(self, file_path, data):
        """
        安全写入JSON文件
        :param file_path: 文件路径
        :param data: 要写入的数据
        :return: bool 是否成功
        """
        if not data:
            _get_logger().debug("数据为空，跳过写入")
            return True
        
        temp_file_path = f"{file_path}.tmp.{int(time.time())}"  # 添加时间戳，避免临时文件冲突
        
        for retry in range(self.max_retries):
            try:
                # 确保目录存在
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # 写入临时文件，使用缓冲区提高写入速度
                with open(temp_file_path, 'w', encoding='utf-8', buffering=8192) as f:
                    # 使用更紧凑的JSON格式，减少文件大小
                    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
                
                # 原子性替换
                import shutil
                shutil.move(temp_file_path, file_path)
                
                # 更新写入状态
                self.last_write_time = time.time()
                self.write_success_count += 1
                self.write_error_count = 0  # 重置错误计数
                
                if retry > 0:
                    _get_logger().info(f"写入JSON文件成功（重试 {retry} 次）: {file_path}")
                else:
                    _get_logger().debug(f"写入JSON文件成功: {file_path} (包含 {len(data)} 条记录)")
                
                return True
                
            except Exception as e:
                _get_logger().error(f"写入JSON文件失败（尝试 {retry+1}/{self.max_retries}）: {e}")
                self.write_error_count += 1
                
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    try:
                        os.remove(temp_file_path)
                    except OSError as e:
                        _get_logger().error(f"删除临时文件失败: {e}")
                
                # 如果不是最后一次重试，等待一段时间后重试
                if retry < self.max_retries - 1:
                    wait_time = (retry + 1) * 2  # 指数退避策略
                    _get_logger().info(f"{wait_time}秒后重试写入")
                    time.sleep(wait_time)
                
        # 所有重试都失败
        _get_logger().error(f"写入JSON文件失败，已达到最大重试次数 ({self.max_retries}次)")
        return False
        
    def get_write_status(self):
        """
        获取写入状态
        :return: dict 写入状态
        """
        return {
            'last_write_time': self.last_write_time,
            'write_error_count': self.write_error_count,
            'write_success_count': self.write_success_count,
            'queue_size': self.write_queue.qsize()
        }
    
    def force_generate(self, initial_data=None):
        """
        强制生成JSON文件（忽略时间间隔限制）
        :param initial_data: 初始数据（可选）
        :return: 文件路径或None
        """
        _get_logger().info("强制生成JSON文件")
        with self.lock:
            self.last_generate_time = 0  # 重置时间，绕过时间检查
            # 如果提供了初始数据，添加到待处理队列
            if initial_data:
                self.pending_data.append(initial_data)
                _get_logger().debug(f"添加初始数据到待处理队列，当前队列长度: {len(self.pending_data)}")
        return self.generate_json_file()
    
    def get_pending_count(self):
        """
        获取待处理数据数量
        :return: int 待处理数据数量
        """
        with self.lock:
            return len(self.pending_data)
    
    def clear_pending_data(self):
        """
        清空待处理数据
        """
        with self.lock:
            count = len(self.pending_data)
            self.pending_data.clear()
            _get_logger().info(f"已清空 {count} 条待处理数据")
    
    def shutdown(self):
        """
        关闭调度器，清理资源
        """
        _get_logger().info("关闭JSON调度器")
        self.write_thread_running = False
        
        # 等待异步写入完成
        try:
            # 处理剩余的待处理数据
            if self.pending_data:
                _get_logger().info(f"处理剩余的 {len(self.pending_data)} 条待处理数据")
                self.generate_json_file()
            
            # 等待写入队列处理完成
            # 注意：Queue.join() 不接受 timeout 参数，使用循环检查方式
            import time
            start_time = time.time()
            timeout = 15
            while not self.write_queue.empty() and time.time() - start_time < timeout:
                time.sleep(0.1)
            # 强制标记所有任务为完成
            try:
                while not self.write_queue.empty():
                    self.write_queue.get(block=False)
                    self.write_queue.task_done()
            except queue.Empty:
                pass
        except Exception as e:
            _get_logger().error(f"关闭调度器时发生异常: {e}")
    
    def reset_status(self):
        """
        重置写入状态
        """
        _get_logger().info("重置JSON调度器状态")
        self.write_error_count = 0  # 重置错误计数
        self.last_write_time = time.time()  # 更新最后写入时间

# 创建全局调度器实例
json_scheduler = JSONScheduler(
    min_interval=60,  # 默认60秒最小间隔
    max_pending=1500,  # 增大待处理队列容量
    batch_size=50  # 批量处理大小
)