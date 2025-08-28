# -*- coding: utf-8 -*-
"""
任务调度器模块
负责定时执行归档任务
"""

import schedule
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Callable, Any

class TaskScheduler:
    """任务调度器类"""
    
    def __init__(self):
        self.is_running = False
        self.scheduler_thread = None
        self.archive_callback = None
        self.status_callback = None
        self.config = None
        
    def start(self, config: Dict[str, Any], archive_callback: Callable = None, 
             status_callback: Callable = None):
        """启动调度器
        
        Args:
            config: 配置字典
            archive_callback: 归档回调函数
            status_callback: 状态更新回调函数
        """
        if self.is_running:
            return
            
        self.config = config
        self.archive_callback = archive_callback
        self.status_callback = status_callback
        
        # 清除之前的任务
        schedule.clear()
        
        # 根据配置设置任务
        self.setup_schedule()
        
        # 启动调度器线程
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        if self.status_callback:
            self.status_callback("调度器已启动")
            
    def stop(self):
        """停止调度器"""
        self.is_running = False
        schedule.clear()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            # 等待线程结束
            self.scheduler_thread.join(timeout=2)
            
        if self.status_callback:
            self.status_callback("调度器已停止")
            
    def setup_schedule(self):
        """根据配置设置调度任务"""
        if not self.config:
            return
            
        frequency = self.config.get('frequency', '每天')
        hour = int(self.config.get('hour', 18))
        minute = int(self.config.get('minute', 0))
        
        time_str = f"{hour:02d}:{minute:02d}"
        
        if frequency == '每小时':
            # 每小时在指定分钟执行
            schedule.every().hour.at(f":{minute:02d}").do(self._execute_archive)
            
        elif frequency == '每天':
            # 每天在指定时间执行
            schedule.every().day.at(time_str).do(self._execute_archive)
            
        elif frequency == '每周':
            # 每周一在指定时间执行
            schedule.every().monday.at(time_str).do(self._execute_archive)
            
        elif frequency == '每月':
            # 每月1号在指定时间执行（简化实现）
            schedule.every().day.at(time_str).do(self._check_monthly_archive)
            
        if self.status_callback:
            self.status_callback(f"已设置{frequency}归档任务，时间：{time_str}")
            
    def _run_scheduler(self):
        """运行调度器的主循环"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                if self.status_callback:
                    self.status_callback(f"调度器错误: {str(e)}")
                time.sleep(5)  # 出错后等待5秒再继续
                
    def _execute_archive(self):
        """执行归档任务"""
        try:
            if self.status_callback:
                self.status_callback("开始执行定时归档...")
                
            if self.archive_callback:
                result = self.archive_callback()
                
                if self.status_callback:
                    if result.get('success', False):
                        count = result.get('count', 0)
                        self.status_callback(f"定时归档完成，处理了 {count} 个文件")
                    else:
                        error = result.get('error', '未知错误')
                        self.status_callback(f"定时归档失败: {error}")
            else:
                if self.status_callback:
                    self.status_callback("归档回调函数未设置")
                    
        except Exception as e:
            if self.status_callback:
                self.status_callback(f"执行归档任务时出错: {str(e)}")
                
    def _check_monthly_archive(self):
        """检查是否需要执行月度归档"""
        # 只在每月1号执行
        if datetime.now().day == 1:
            self._execute_archive()
            
    def get_next_run_time(self) -> str:
        """获取下次运行时间
        
        Returns:
            下次运行时间的字符串表示
        """
        try:
            if not self.is_running or not schedule.jobs:
                return "未设置"
                
            next_run = schedule.next_run()
            if next_run:
                return next_run.strftime('%Y-%m-%d %H:%M:%S')
            else:
                return "未知"
                
        except Exception as e:
            return f"获取失败: {str(e)}"
            
    def get_schedule_info(self) -> Dict[str, Any]:
        """获取调度信息
        
        Returns:
            调度信息字典
        """
        info = {
            'is_running': self.is_running,
            'job_count': len(schedule.jobs),
            'next_run_time': self.get_next_run_time(),
            'jobs': []
        }
        
        try:
            for job in schedule.jobs:
                job_info = {
                    'interval': job.interval,
                    'unit': job.unit,
                    'at_time': str(job.at_time) if job.at_time else None,
                    'next_run': job.next_run.strftime('%Y-%m-%d %H:%M:%S') if job.next_run else None
                }
                info['jobs'].append(job_info)
                
        except Exception as e:
            info['error'] = str(e)
            
        return info
        
    def update_schedule(self, config: Dict[str, Any]):
        """更新调度配置
        
        Args:
            config: 新的配置字典
        """
        self.config = config
        
        if self.is_running:
            # 重新设置调度
            schedule.clear()
            self.setup_schedule()
            
            if self.status_callback:
                self.status_callback("调度配置已更新")
                
    def force_run(self):
        """强制执行一次归档任务"""
        if self.status_callback:
            self.status_callback("手动触发归档任务...")
            
        # 在新线程中执行，避免阻塞
        thread = threading.Thread(target=self._execute_archive, daemon=True)
        thread.start()
        
    def get_time_until_next_run(self) -> str:
        """获取距离下次运行的时间
        
        Returns:
            时间差的字符串表示
        """
        try:
            if not self.is_running or not schedule.jobs:
                return "未设置"
                
            next_run = schedule.next_run()
            if next_run:
                now = datetime.now()
                time_diff = next_run - now
                
                if time_diff.total_seconds() < 0:
                    return "即将执行"
                    
                days = time_diff.days
                hours, remainder = divmod(time_diff.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                
                if days > 0:
                    return f"{days}天{hours}小时{minutes}分钟"
                elif hours > 0:
                    return f"{hours}小时{minutes}分钟"
                else:
                    return f"{minutes}分钟"
            else:
                return "未知"
                
        except Exception as e:
            return f"计算失败: {str(e)}"
            
    def is_schedule_active(self) -> bool:
        """检查调度是否处于活动状态
        
        Returns:
            调度是否活动
        """
        return self.is_running and len(schedule.jobs) > 0
        
    def pause_schedule(self):
        """暂停调度（保持线程运行但不执行任务）"""
        schedule.clear()
        
        if self.status_callback:
            self.status_callback("调度已暂停")
            
    def resume_schedule(self):
        """恢复调度"""
        if self.config:
            self.setup_schedule()
            
            if self.status_callback:
                self.status_callback("调度已恢复")
                
    def add_one_time_task(self, delay_minutes: int):
        """添加一次性任务
        
        Args:
            delay_minutes: 延迟执行的分钟数
        """
        def one_time_archive():
            self._execute_archive()
            # 任务执行后自动移除
            return schedule.CancelJob
            
        target_time = datetime.now() + timedelta(minutes=delay_minutes)
        time_str = target_time.strftime('%H:%M')
        
        schedule.every().day.at(time_str).do(one_time_archive)
        
        if self.status_callback:
            self.status_callback(f"已添加一次性任务，将在{delay_minutes}分钟后执行")
            
    def get_execution_history(self) -> list:
        """获取执行历史（简化实现）
        
        Returns:
            执行历史列表
        """
        # 这里可以实现执行历史的记录和返回
        # 简化实现，返回空列表
        return []
        
    def cleanup(self):
        """清理资源"""
        self.stop()
        self.archive_callback = None
        self.status_callback = None
        self.config = None