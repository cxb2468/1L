# 生成黄金价格监控HTML文件
import os
import sys
from datetime import datetime

# 确保可以导入项目模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import DEFAULT_GOLD_PRICE, DEFAULT_PRICE_GAP_HIGH, DEFAULT_PRICE_GAP_LOW, ENABLE_AI_ANALYSIS
from logger.logger_config import get_logger

logger = get_logger(__name__)
class HTMLGenerator:
    """
    黄金价格HTML生成器
    """
    def __init__(self):
        # 获取当前文件的目录
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 检查是否在PyInstaller打包环境中
        is_pyinstaller = getattr(sys, 'frozen', False)
        
        if is_pyinstaller:
            # 在PyInstaller环境中，模板文件应该在当前工作目录中
            self.template_path = os.path.join(os.getcwd(), 'templates', 'gold_price_template.html')
            self.output_path = os.path.join(os.getcwd(), 'index.html')
        else:
            # 在开发环境中，使用原始路径
            self.template_path = os.path.join(base_dir, 'templates', 'gold_price_template.html')
            self.output_path = os.path.join(base_dir, 'index.html')
        
        # 确保templates目录存在
        template_dir = os.path.dirname(self.template_path)
        if not os.path.exists(template_dir) and not is_pyinstaller:
            os.makedirs(template_dir, exist_ok=True)
        
    def generate_html(self, price_data):
        """
        生成HTML文件
        :param price_data: 包含价格信息的字典
        :return: str 生成的HTML文件路径
        """
        try:
            # 读取模板文件
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # 准备模板数据
            template_data = self._prepare_template_data(price_data)
            
            # 调试信息
            logger.debug(f"enable_ai_analysis = {template_data.get('enable_ai_analysis', 'NOT_SET')}")
            logger.debug(f"ai_analysis_section 长度 = {len(template_data.get('ai_analysis_section', ''))}")
            if template_data.get('ai_analysis_section'):
                logger.debug(f"ai_analysis_section 内容预览 = {template_data['ai_analysis_section'][:100]}...")
            
            # 直接替换模板变量
            html_content = template
            for key, value in template_data.items():
                placeholder = f"{{{{ {key} }}}}"
                html_content = html_content.replace(placeholder, str(value))
            
            # 写入HTML文件
            with open(self.output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return self.output_path
        except (IOError, OSError, KeyError) as e:
            logger.error(f"生成HTML文件失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return None
    
    def _process_template_conditions(self, template_content, template_data):
        """
        处理模板中的条件语句
        :param template_content: 模板内容
        :param template_data: 模板数据
        :return: 处理后的模板内容
        """
        import re
        
        # 处理 {% if enable_ai_analysis %} ... {% endif %} 条件
        pattern = r'{%\s*if\s+enable_ai_analysis\s*%}(.*?){%\s*endif\s*%}'
        
        def replace_condition(match):
            content_inside = match.group(1)
            # 检查AI分析是否启用
            if template_data.get('enable_ai_analysis', False):
                return content_inside
            else:
                return ''  # 条件不满足时返回空字符串
        
        # 执行替换
        processed_content = re.sub(pattern, replace_condition, template_content, flags=re.DOTALL)
        return processed_content
    
    def _prepare_template_data(self, price_data):
        """
        准备模板数据
        :param price_data: 包含价格信息的字典
        :return: dict 模板数据
        """
        import config  # 在方法内部导入以获取最新值
        
        # 检查是否存在错误信息
        if 'error' in price_data:
            # 出现错误时的模板数据
            error_msg = price_data['error']
            # 根据错误类型设置不同的样式
            if '禁止推送' in error_msg:
                alert_class = 'alert-blocked'
                alert_title = '推送已禁用'
            else:
                alert_class = 'alert-error'
                alert_title = '系统错误'
            
            return {
                'update_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'current_price': '--',
                'base_price': '--',
                'high_threshold': '--',
                'low_threshold': '--',
                'trend_text': '系统维护中',
                'trend_arrow': '⚠',
                'trend_class': 'trend-error',
                'data_source': '系统维护',
                'current_year': datetime.now().year,
                'alerts': f"<div class='alert-item {alert_class}'><div class='alert-title'>{alert_title}</div><div class='alert-desc'>{error_msg}</div></div>"
            }
        
        # 获取当前价格
        current_price = price_data.get('current_price', DEFAULT_GOLD_PRICE)
        base_price = price_data.get('base_price', DEFAULT_GOLD_PRICE)
        
        # 计算预警阈值
        high_threshold = base_price + DEFAULT_PRICE_GAP_HIGH
        low_threshold = base_price - DEFAULT_PRICE_GAP_LOW
        
        # 计算价格趋势
        trend_text = "价格稳定"
        trend_arrow = "→"
        trend_class = "trend-stable"
        
        if 'last_price' in price_data and price_data['last_price'] is not None:
            price_diff = current_price - price_data['last_price']
            if price_diff > 0:
                trend_text = f"上涨 {abs(price_diff):.2f} 元"
                trend_arrow = "↑"
                trend_class = "trend-up"
            elif price_diff < 0:
                trend_text = f"下跌 {abs(price_diff):.2f} 元"
                trend_arrow = "↓"
                trend_class = "trend-down"
        
        # 准备预警信息
        alerts = []
        if current_price >= high_threshold:
            alerts.append({
                'class': 'alert-high',
                'title': '高价预警',
                'description': f'当前黄金价格 ¥{current_price:.2f}/克 已超过预警阈值 ¥{high_threshold:.2f}/克'
            })
        if current_price <= low_threshold:
            alerts.append({
                'class': 'alert-low',
                'title': '低价预警',
                'description': f'当前黄金价格 ¥{current_price:.2f}/克 已低于预警阈值 ¥{low_threshold:.2f}/克'
            })
        
        # 处理预警信息，生成HTML字符串
        alerts_html = ""
        if alerts:
            for alert in alerts:
                alerts_html += f"<div class='alert-item {alert['class']}'>"
                alerts_html += f"<div class='alert-title'>{alert['title']}</div>"
                alerts_html += f"<div class='alert-desc'>{alert['description']}</div>"
                alerts_html += "</div>"
        else:
            alerts_html = "<div class='alert-item'><div class='alert-title'>暂无预警</div><div class='alert-desc'>当前黄金价格处于正常波动范围</div></div>"
        
        # 获取AI分析建议（如果有）
        ai_analysis = price_data.get('ai_analysis', '')
        
        # 获取推送错误信息（如果有）
        push_error = price_data.get('push_error', '')
        
        # 动态获取当前使用的数据源名称
        try:
            import config
            # 获取启用的数据源
            enabled_sources = [source for source in config.GOLD_PRICE_SOURCES if source.get('enabled', True)]
            if enabled_sources:
                # 按排序获取第一个启用的数据源作为当前数据源
                sorted_sources = sorted(enabled_sources, key=lambda x: x.get('sort_order', 999))
                data_source_name = sorted_sources[0]['name']
            else:
                data_source_name = '系统维护'
        except Exception as e:
            logger.warning(f"获取数据源名称失败: {e}")
            data_source_name = '系统维护'
        
        # 模板数据
        template_data = {
            'update_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'current_price': f"{current_price:.2f}",
            'base_price': f"{base_price:.2f}",
            'high_threshold': f"{high_threshold:.2f}",
            'low_threshold': f"{low_threshold:.2f}",
            'default_gold_price': f"{DEFAULT_GOLD_PRICE:.2f}",
            'trend_text': trend_text,
            'trend_arrow': trend_arrow,
            'trend_class': trend_class,
            'data_source': data_source_name,
            'current_year': datetime.now().year,
            'alerts': alerts_html
        }
        
        # 如果存在推送错误，添加到警告信息中
        if push_error:
            push_error_alert = f"<div class='alert-item alert-warning'><div class='alert-title'>微信推送警告</div><div class='alert-desc'>推送失败: {push_error}</div></div>"
            # 将推送错误添加到现有警告前面
            template_data['alerts'] = push_error_alert + template_data['alerts']
        
        # 根据AI开关状态准备AI分析区域的HTML
        if config.config.ENABLE_AI_ANALYSIS and ai_analysis:
            template_data['ai_analysis_section'] = f'''
        <section class="trend-section">
            <h2 style="margin-bottom: 20px; color: #333;">AI分析建议</h2>
            <div class="trend-item">
                <div class="trend-label">专业建议</div>
                <div class="trend-value trend-stable">{ai_analysis}</div>
            </div>
        </section>'''
            template_data['ai_analysis'] = ai_analysis
        else:
            template_data['ai_analysis_section'] = ''
            template_data['ai_analysis'] = 'AI分析功能已禁用'
            
        return template_data

