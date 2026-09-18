"""
生产排产系统 - 工单排序与冲突检测
功能：
1. 根据订单生成生产工单（含工艺路线）
2. 工作站时间冲突检测（精确到部分重叠）
3. 生成甘特图（生产排序图）
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import uuid
import os

# ============================================================
#  尝试设置中文字体（兼容 Windows / macOS / Linux）
# ============================================================
def setup_chinese_font():
    """自动检测可用的中文字体"""
    font_candidates = [
        "SimHei",           # Windows 黑体
        "Microsoft YaHei",  # Windows 微软雅黑
        "PingFang SC",      # macOS
        "Noto Sans CJK SC", # Linux
        "WenQuanYi Micro Hei",
    ]
    available_fonts = {f.name for f in font_manager.fontManager.ttflist}
    for font_name in font_candidates:
        if font_name in available_fonts:
            plt.rcParams["font.sans-serif"] = [font_name]
            plt.rcParams["axes.unicode_minus"] = False
            print(f"[字体] 使用: {font_name}")
            return
    print("[字体] 警告: 未找到中文字体，图表中文可能显示为方块")

setup_chinese_font()


# ============================================================
#  1. 数据模型定义
# ============================================================
@dataclass
class ProcessStep:
    """工序定义"""
    step_id: int              # 工序序号
    name: str                 # 工序名称，如 "工序1"
    workstation: str          # 使用的工作站，如 "工作站1"
    duration_hours: float     # 该工序标准工时（小时）


@dataclass
class ProcessRoute:
    """工艺路线"""
    product_name: str         # 产品名称
    steps: List[ProcessStep]  # 工序列表（按顺序）


@dataclass
class Order:
    """订单"""
    order_id: str             # 订单编号
    product_name: str         # 产品名称
    quantity: int             # 数量
    priority: int = 1         # 优先级（数字越小越优先）
    planned_start: Optional[datetime] = None  # 计划开始时间


@dataclass
class ScheduledTask:
    """已排程的任务（一个工序的一个实例）"""
    task_id: str              # 任务唯一ID
    work_order_id: str        # 所属工单ID
    order_id: str             # 所属订单ID
    step: ProcessStep         # 工序信息
    start_time: datetime      # 实际开始时间
    end_time: datetime        # 实际结束时间
    workstation: str          # 工作站


@dataclass
class WorkOrder:
    """生产工单"""
    work_order_id: str        # 工单编号
    order_id: str             # 来源订单编号
    product_name: str         # 产品名称
    quantity: int             # 生产数量
    tasks: List[ScheduledTask] = field(default_factory=list)
    status: str = "待排程"     # 待排程 / 已排程 / 冲突


# ============================================================
#  2. 排产引擎（核心）
# ============================================================
class ProductionScheduler:
    """生产排产调度器"""

    def __init__(self):
        self.process_routes: dict[str, ProcessRoute] = {}  # 产品名 -> 工艺路线
        self.orders: List[Order] = []
        self.work_orders: List[WorkOrder] = []
        self.scheduled_tasks: List[ScheduledTask] = []  # 所有已排程任务（全局）
        self.conflicts: List[dict] = []                  # 冲突记录

    # ---------- 注册工艺路线 ----------
    def register_route(self, route: ProcessRoute):
        self.process_routes[route.product_name] = route
        print(f"[工艺路线] 已注册: {route.product_name} -> "
              f"{' -> '.join(s.name for s in route.steps)} -> 结束")

    # ---------- 添加订单 ----------
    def add_order(self, order: Order):
        self.orders.append(order)
        print(f"[订单] 已添加: {order.order_id} | 产品={order.product_name} "
              f"| 数量={order.quantity} | 优先级={order.priority}")

    # ---------- 生成工单（不含排程） ----------
    def generate_work_orders(self) -> List[WorkOrder]:
        self.work_orders.clear()
        # 按优先级排序
        sorted_orders = sorted(self.orders, key=lambda o: o.priority)
        for order in sorted_orders:
            wo = WorkOrder(
                work_order_id=f"WO-{uuid.uuid4().hex[:8].upper()}",
                order_id=order.order_id,
                product_name=order.product_name,
                quantity=order.quantity,
                status="待排程",
            )
            self.work_orders.append(wo)
            print(f"[工单] 已生成: {wo.work_order_id} <- 订单 {order.order_id}")
        return self.work_orders

    # ---------- 核心：检测时间重叠 ----------
    @staticmethod
    def _is_overlapping(start1: datetime, end1: datetime,
                        start2: datetime, end2: datetime) -> bool:
        """
        判断两个时间段是否存在重叠（含部分重叠）
        重叠条件：start1 < end2 AND start2 < end1
        """
        return start1 < end2 and start2 < end1

    def check_conflict(self, workstation: str,
                       start_time: datetime,
                       end_time: datetime,
                       exclude_task_id: str = None) -> Optional[ScheduledTask]:
        """
        检测指定工作站在 [start_time, end_time] 是否与已有任务冲突
        返回冲突的任务对象，无冲突返回 None
        """
        for task in self.scheduled_tasks:
            if task.task_id == exclude_task_id:
                continue
            if task.workstation != workstation:
                continue
            if self._is_overlapping(start_time, end_time,
                                    task.start_time, task.end_time):
                return task  # 发现冲突
        return None

    # ---------- 自动排程（贪心算法） ----------
    def auto_schedule(self):
        """
        自动排程逻辑：
        1. 按优先级遍历工单
        2. 每个工单按工序顺序排程
        3. 每道工序：找到对应工作站最早的可用时间段
        4. 同时保证：当前工序的开始时间 >= 上一道工序的结束时间（工艺约束）
        """
        self.scheduled_tasks.clear()
        self.conflicts.clear()

        # 按优先级排序工单
        sorted_wos = sorted(self.work_orders,
                            key=lambda wo: next(
                                (o.priority for o in self.orders
                                 if o.order_id == wo.order_id), 99))

        for wo in sorted_wos:
            route = self.process_routes.get(wo.product_name)
            if not route:
                print(f"[错误] 未找到 {wo.product_name} 的工艺路线")
                wo.status = "冲突"
                continue

            order = next((o for o in self.orders if o.order_id == wo.order_id), None)
            # 上一道工序的结束时间（工艺约束）
            prev_end_time = order.planned_start or datetime(2026, 7, 27, 8, 0)

            for step in route.steps:
                # 从「上一道工序结束时间」开始，寻找工作站空闲时段
                candidate_start = prev_end_time
                scheduled = False

                # 尝试最多 100 次偏移（每次偏移 0.5 小时）
                for attempt in range(100):
                    candidate_end = candidate_start + timedelta(hours=step.duration_hours)

                    conflict_task = self.check_conflict(
                        workstation=step.workstation,
                        start_time=candidate_start,
                        end_time=candidate_end,
                    )

                    if conflict_task is None:
                        # 无冲突，可以排程
                        task = ScheduledTask(
                            task_id=f"T-{uuid.uuid4().hex[:6].upper()}",
                            work_order_id=wo.work_order_id,
                            order_id=wo.order_id,
                            step=step,
                            start_time=candidate_start,
                            end_time=candidate_end,
                            workstation=step.workstation,
                        )
                        wo.tasks.append(task)
                        self.scheduled_tasks.append(task)
                        prev_end_time = candidate_end
                        scheduled = True
                        break
                    else:
                        # 有冲突，跳到冲突任务结束后再尝试
                        candidate_start = conflict_task.end_time

                if not scheduled:
                    wo.status = "冲突"
                    print(f"[冲突] 工单 {wo.work_order_id} 的 {step.name} "
                          f"无法在 {step.workstation} 上排程!")

            if wo.status != "冲突":
                wo.status = "已排程"
                print(f"[排程完成] 工单 {wo.work_order_id} 所有工序已排程")

    # ---------- 手动排程（带冲突检测） ----------
    def manual_schedule_task(self, work_order_id: str, step_index: int,
                             start_time: datetime) -> Tuple[bool, str]:
        """
        手动为某个工单的某道工序指定开始时间
        返回 (是否成功, 消息)
        """
        wo = next((w for w in self.work_orders
                   if w.work_order_id == work_order_id), None)
        if not wo:
            return False, f"工单 {work_order_id} 不存在"

        route = self.process_routes.get(wo.product_name)
        if not route or step_index >= len(route.steps):
            return False, "工序索引无效"

        step = route.steps[step_index]
        end_time = start_time + timedelta(hours=step.duration_hours)

        conflict = self.check_conflict(step.workstation, start_time, end_time)
        if conflict:
            msg = (f"❌ 冲突！该工序 [{step.name}] 的工作站 [{step.workstation}] "
                   f"在 {start_time.strftime('%m-%d %H:%M')}~{end_time.strftime('%m-%d %H:%M')} "
                   f"时段已被工单 [{conflict.work_order_id}] "
                   f"(订单 {conflict.order_id}) 引用，请重新选择！")
            self.conflicts.append({
                "work_order_id": work_order_id,
                "step": step.name,
                "workstation": step.workstation,
                "conflict_with": conflict.work_order_id,
                "time_range": f"{start_time} ~ {end_time}",
            })
            return False, msg

        task = ScheduledTask(
            task_id=f"T-{uuid.uuid4().hex[:6].upper()}",
            work_order_id=work_order_id,
            order_id=wo.order_id,
            step=step,
            start_time=start_time,
            end_time=end_time,
            workstation=step.workstation,
        )
        wo.tasks.append(task)
        self.scheduled_tasks.append(task)
        return True, (f"✅ 排程成功: {step.name} @ {step.workstation} "
                      f"{start_time.strftime('%m-%d %H:%M')}~{end_time.strftime('%m-%d %H:%M')}")


    # ============================================================
    #  3. 甘特图可视化
    # ============================================================
    def plot_gantt_chart(self, save_path: str = "gantt_chart.png"):
        """生成生产排序甘特图"""
        if not self.scheduled_tasks:
            print("[警告] 无已排程任务，无法生成甘特图")
            return

        # 按工作站分组
        workstations = sorted(set(t.workstation for t in self.scheduled_tasks))
        colors = [
            "#4E79A7", "#F28E2B", "#E15759", "#76B7B2",
            "#59A14F", "#EDC948", "#B07AA1", "#FF9DA7",
        ]
        # 为每个工单分配颜色
        wo_ids = sorted(set(t.work_order_id for t in self.scheduled_tasks))
        wo_color_map = {wid: colors[i % len(colors)] for i, wid in enumerate(wo_ids)}

        fig, ax = plt.subplots(figsize=(16, max(4, len(workstations) * 1.8)))

        bar_height = 0.6
        y_positions = {ws: i for i, ws in enumerate(workstations)}

        for task in self.scheduled_tasks:
            y = y_positions[task.workstation]
            duration = (task.end_time - task.start_time).total_seconds() / 3600
            color = wo_color_map[task.work_order_id]

            bar = ax.barh(
                y, duration, left=task.start_time, height=bar_height,
                color=color, edgecolor="white", linewidth=1.2, alpha=0.88,
            )

            # 在条形上标注文字
            label = f"{task.order_id}\n{task.step.name}"
            mid_time = task.start_time + (task.end_time - task.start_time) / 2
            ax.text(mid_time, y, label, ha="center", va="center",
                    fontsize=8, fontweight="bold", color="white")

        # Y轴设置
        ax.set_yticks(range(len(workstations)))
        ax.set_yticklabels(workstations, fontsize=12, fontweight="bold")
        ax.set_xlabel("时间", fontsize=12)
        ax.set_title("生产排产甘特图（Gantt Chart）", fontsize=16, fontweight="bold", pad=15)

        # X轴时间格式
        import matplotlib.dates as mdates
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M"))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        fig.autofmt_xdate(rotation=0, ha="center")

        # 网格
        ax.grid(axis="x", alpha=0.3, linestyle="--")
        ax.set_axisbelow(True)

        # 图例
        legend_patches = [
            mpatches.Patch(facecolor=wo_color_map[wid], label=f"{wid}")
            for wid in wo_ids
        ]
        ax.legend(handles=legend_patches, title="工单", loc="upper right",
                  fontsize=9, title_fontsize=10)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"[甘特图] 已保存至: {os.path.abspath(save_path)}")
        plt.show()

    # ---------- 打印排程结果 ----------
    def print_schedule(self):
        print("\n" + "=" * 80)
        print("📋 生产排程结果汇总")
        print("=" * 80)
        for wo in self.work_orders:
            order = next((o for o in self.orders if o.order_id == wo.order_id), None)
            print(f"\n🔹 工单: {wo.work_order_id} | 订单: {wo.order_id} "
                  f"| 产品: {wo.product_name} | 数量: {wo.quantity} | 状态: {wo.status}")
            for task in sorted(wo.tasks, key=lambda t: t.start_time):
                print(f"   ├─ {task.step.name} @ {task.workstation}: "
                      f"{task.start_time.strftime('%Y-%m-%d %H:%M')} ~ "
                      f"{task.end_time.strftime('%Y-%m-%d %H:%M')} "
                      f"({task.step.duration_hours}h)")


# ============================================================
#  4. 演示运行
# ============================================================
def main():
    scheduler = ProductionScheduler()

    # ---- 4.1 定义工艺路线 ----
    route_a = ProcessRoute(
        product_name="产品A",
        steps=[
            ProcessStep(step_id=1, name="工序1", workstation="工作站1", duration_hours=3),
            ProcessStep(step_id=2, name="工序2", workstation="工作站2", duration_hours=2),
            ProcessStep(step_id=3, name="工序3", workstation="工作站3", duration_hours=2),
        ],
    )
    scheduler.register_route(route_a)

    # ---- 4.2 创建 4 个订单 ----
    base_time = datetime(2026, 7, 27, 8, 0)  # 今天 8:00 开始

    orders = [
        Order("ORD-001", "产品A", 100, priority=1, planned_start=base_time),
        Order("ORD-002", "产品A", 200, priority=2, planned_start=base_time),
        Order("ORD-003", "产品A", 150, priority=3, planned_start=base_time),
        Order("ORD-004", "产品A", 80,  priority=4, planned_start=base_time),
    ]
    for o in orders:
        scheduler.add_order(o)

    # ---- 4.3 生成工单 ----
    print("\n--- 生成工单 ---")
    scheduler.generate_work_orders()

    # ---- 4.4 自动排程（自动避让冲突） ----
    print("\n--- 自动排程 ---")
    scheduler.auto_schedule()
    scheduler.print_schedule()

    # ---- 4.5 演示手动排程的冲突检测 ----
    print("\n\n--- 手动排程冲突检测演示 ---")
    # 尝试把 ORD-003 的工序1 手动排到和 ORD-001 重叠的时间段
    first_wo = scheduler.work_orders[0]  # ORD-001 的工单
    third_wo = scheduler.work_orders[2]  # ORD-003 的工单

    # 故意设一个与已有任务重叠的时间
    conflict_time = datetime(2026, 7, 27, 9, 0)  # 与 ORD-001 的工序1 重叠
    success, msg = scheduler.manual_schedule_task(
        third_wo.work_order_id, step_index=0, start_time=conflict_time
    )
    print(msg)

    # ---- 4.6 生成甘特图 ----
    print("\n--- 生成甘特图 ---")
    scheduler.plot_gantt_chart("production_gantt.png")


if __name__ == "__main__":
    main()