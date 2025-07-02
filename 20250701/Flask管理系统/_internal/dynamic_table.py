from field_config import get_field_config, get_visible_fields, get_searchable_fields
from flask import render_template_string

class DynamicTableGenerator:
    """动态表格生成器"""
    
    def __init__(self, module_name):
        self.module_name = module_name
        self.config = get_field_config(module_name)
        self.fields = self.config.get('fields', [])
    
    def generate_table_html(self, data, page_info=None):
        """生成表格HTML"""
        visible_fields = get_visible_fields(self.module_name)
        
        # 生成表头
        headers = []
        for field in visible_fields:
            headers.append(field['label'])
        
        # 生成表格行
        rows = []
        for item in data:
            row = []
            for field in visible_fields:
                field_name = field['name']
                field_type = field['type']
                value = getattr(item, field_name, '')
                
                # 根据字段类型格式化显示
                formatted_value = self._format_field_value(value, field_type, field, item)
                row.append(formatted_value)
            rows.append(row)
        
        # 生成HTML
        html = self._generate_html_table(headers, rows, page_info)
        return html
    
    def _format_field_value(self, value, field_type, field_config, item):
        """格式化字段值"""
        if value is None:
            return ''
        
        if field_type == 'datetime':
            if hasattr(value, 'strftime'):
                from datetime import timezone, timedelta
                # 转换为北京时间
                if value.tzinfo is None:
                    # 假设是UTC时间
                    utc_tz = timezone.utc
                    dt = value.replace(tzinfo=utc_tz)
                else:
                    dt = value
                beijing_tz = timezone(timedelta(hours=8))
                dt = dt.astimezone(beijing_tz)
                return dt.strftime('%Y-%m-%d %H:%M')
            return str(value)
        elif field_type == 'date':
            if hasattr(value, 'strftime'):
                from datetime import timezone, timedelta
                # 转换为北京时间
                if value.tzinfo is None:
                    # 假设是UTC时间
                    utc_tz = timezone.utc
                    dt = value.replace(tzinfo=utc_tz)
                else:
                    dt = value
                beijing_tz = timezone(timedelta(hours=8))
                dt = dt.astimezone(beijing_tz)
                return dt.strftime('%Y-%m-%d')
            return str(value)
        elif field_type == 'boolean':
            return '是' if value else '否'
        elif field_type == 'file':
            if value:
                return f'<a href="/{self.module_name}/download/{value}" target="_blank" class="btn btn-link btn-sm">查看</a>'
            return ''
        elif field_type == 'select':
            options = field_config.get('options', [])
            if value in options:
                return value
            return str(value)
        else:
            return str(value)
    
    def _generate_html_table(self, headers, rows, page_info):
        """生成HTML表格"""
        html_template = """
        <div class="table-responsive">
            <table class="table table-bordered" style="min-width: 1000px;">
                <thead>
                    <tr>
                        <th>序号</th>
                        {% for header in headers %}
                        <th>{{ header }}</th>
                        {% endfor %}
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in rows %}
                    <tr>
                        <td>{{ loop.index + (page_info.page - 1) * page_info.per_page if page_info else loop.index }}</td>
                        {% for cell in row %}
                        <td>{{ cell | safe }}</td>
                        {% endfor %}
                        <td>
                            <a href="/{{ module_name }}/edit/{{ row_data[loop.index0].id }}" class="btn btn-sm btn-primary">编辑</a>
                            <form action="/{{ module_name }}/delete/{{ row_data[loop.index0].id }}" method="post" style="display:inline;" onsubmit="return confirm('确定要删除吗？');">
                                <button class="btn btn-sm btn-danger">删除</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        """
        
        return render_template_string(html_template, 
                                    headers=headers, 
                                    rows=rows, 
                                    module_name=self.module_name,
                                    row_data=page_info.items if page_info else [],
                                    page_info=page_info)
    
    def generate_search_form(self):
        """生成搜索表单"""
        searchable_fields = get_searchable_fields(self.module_name)
        
        if not searchable_fields:
            return ""
        
        html_template = """
        <form class="form-inline mr-2" method="get" action="">
            <select name="field" class="form-control mr-2">
                {% for field in searchable_fields %}
                <option value="{{ field.name }}" {% if selected_field == field.name %}selected{% endif %}>{{ field.label }}</option>
                {% endfor %}
            </select>
            <input type="text" name="q" class="form-control mr-2" value="{{ search_query }}" placeholder="请输入关键词">
            <button class="btn btn-info mr-2">搜索</button>
        </form>
        """
        
        return render_template_string(html_template, 
                                    searchable_fields=searchable_fields,
                                    selected_field=request.args.get('field', ''),
                                    search_query=request.args.get('q', ''))
    
    def generate_import_export_buttons(self):
        """生成导入导出按钮"""
        table_config = self.config.get('table_config', {})
        
        if not table_config.get('exportable') and not table_config.get('importable'):
            return ""
        
        html_template = """
        <form class="form-inline mr-2" method="post" action="/{{ module_name }}/import" enctype="multipart/form-data" id="importForm">
            {% if table_config.exportable %}
            <a href="/{{ module_name }}/export" class="btn btn-secondary mr-2" id="exportBtn">导出</a>
            {% endif %}
            {% if table_config.importable %}
            <a href="/{{ module_name }}/template" class="btn btn-outline-info mr-2">下载导入模板</a>
            <input type="file" name="import_file" id="importFile" style="display:none;">
            <button type="button" class="btn btn-primary mr-2" id="importBtn">导入</button>
            <span id="importProgress" style="margin-left:10px;display:none;">正在导入，请稍候...</span>
            {% endif %}
            <span id="exportProgress" style="margin-left:10px;display:none;">正在导出，请稍候...</span>
        </form>
        """
        
        return render_template_string(html_template, 
                                    module_name=self.module_name,
                                    table_config=table_config)

def create_dynamic_view(module_name, model_class, blueprint):
    """创建动态视图函数"""
    
    @blueprint.route('/')
    @login_required
    @permission_required(module_name)
    def dynamic_list():
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        q = request.args.get('q', '').strip()
        field = request.args.get('field', '')
        
        # 构建查询
        query = model_class.query
        
        # 搜索过滤
        if q and field:
            searchable_fields = get_searchable_fields(module_name)
            field_config = next((f for f in searchable_fields if f['name'] == field), None)
            if field_config:
                field_name = field_config['name']
                query = query.filter(getattr(model_class, field_name).like(f'%{q}%'))
        
        # 分页
        pagination = query.order_by(model_class.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 生成动态表格
        table_generator = DynamicTableGenerator(module_name)
        table_html = table_generator.generate_table_html(pagination.items, pagination)
        search_form = table_generator.generate_search_form()
        import_export_buttons = table_generator.generate_import_export_buttons()
        
        return render_template('dynamic_list.html',
                             module_name=module_name,
                             table_html=table_html,
                             search_form=search_form,
                             import_export_buttons=import_export_buttons,
                             pagination=pagination,
                             per_page=per_page,
                             q=q,
                             field=field) 