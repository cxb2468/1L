from models import FieldConfig, FieldValue
from flask import request
import json

class DynamicFieldManager:
    """动态字段管理器"""
    
    def __init__(self, module_name):
        self.module_name = module_name
        self.fields = self._load_fields()
    
    def _load_fields(self):
        """加载字段配置"""
        fields = FieldConfig.query.filter_by(
            module_name=self.module_name, 
            is_visible=True
        ).order_by(FieldConfig.field_order).all()
        
        field_list = []
        for field in fields:
            field_data = {
                'id': field.id,
                'name': field.field_name,
                'label': field.field_label,
                'type': field.field_type,
                'required': field.is_required,
                'searchable': field.is_searchable,
                'exportable': field.is_exportable,
                'importable': field.is_importable,
                'is_visible': field.is_visible,
                'width': field.field_width,
                'order': field.field_order
            }
            
            # 解析字段选项
            if field.field_options:
                try:
                    field_data['options'] = json.loads(field.field_options)
                except:
                    field_data['options'] = []
            else:
                field_data['options'] = []
            
            # 解析验证规则
            if field.validation_rules:
                try:
                    field_data['validation'] = json.loads(field.validation_rules)
                except:
                    field_data['validation'] = {}
            else:
                field_data['validation'] = {}
            
            field_list.append(field_data)
        
        return field_list
    
    def get_visible_fields(self):
        """获取可见字段"""
        return self.fields
    
    def get_searchable_fields(self):
        """获取可搜索字段"""
        return [f for f in self.fields if f['searchable']]
    
    def get_exportable_fields(self):
        """获取可导出字段"""
        return [f for f in self.fields if f['exportable']]
    
    def get_importable_fields(self):
        """获取可导入字段"""
        return [f for f in self.fields if f['importable']]
    
    def get_field_by_name(self, field_name):
        """根据字段名获取字段配置"""
        for field in self.fields:
            if field['name'] == field_name:
                return field
        return None
    
    def get_field_value(self, record_id, field_name):
        """获取字段值"""
        field_value = FieldValue.query.filter_by(
            module_name=self.module_name,
            record_id=record_id,
            field_name=field_name
        ).first()
        return field_value.field_value if field_value else ''
    
    def set_field_value(self, record_id, field_name, value):
        """设置字段值"""
        field_value = FieldValue.query.filter_by(
            module_name=self.module_name,
            record_id=record_id,
            field_name=field_name
        ).first()
        
        if field_value:
            field_value.field_value = value
        else:
            field_value = FieldValue(
                module_name=self.module_name,
                record_id=record_id,
                field_name=field_name,
                field_value=value
            )
            from extensions import db
            db.session.add(field_value)
        
        from extensions import db
        db.session.commit()
    
    def format_field_value(self, value, field_config):
        """格式化字段值显示"""
        if value is None or value == '':
            return ''
        
        field_type = field_config['type']
        
        if field_type == 'datetime':
            try:
                from datetime import datetime, timezone, timedelta
                if isinstance(value, str):
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    # 转换为北京时间
                    beijing_tz = timezone(timedelta(hours=8))
                    dt = dt.astimezone(beijing_tz)
                    return dt.strftime('%Y-%m-%d %H:%M')
                elif hasattr(value, 'strftime'):
                    # 如果是datetime对象，转换为北京时间
                    if value.tzinfo is None:
                        # 假设是UTC时间
                        utc_tz = timezone.utc
                        dt = value.replace(tzinfo=utc_tz)
                    else:
                        dt = value
                    beijing_tz = timezone(timedelta(hours=8))
                    dt = dt.astimezone(beijing_tz)
                    return dt.strftime('%Y-%m-%d %H:%M')
            except:
                return str(value)
        elif field_type == 'date':
            try:
                from datetime import datetime, timezone, timedelta
                if isinstance(value, str):
                    dt = datetime.fromisoformat(value)
                    # 转换为北京时间
                    beijing_tz = timezone(timedelta(hours=8))
                    dt = dt.astimezone(beijing_tz)
                    return dt.strftime('%Y-%m-%d')
                elif hasattr(value, 'strftime'):
                    # 如果是datetime对象，转换为北京时间
                    if value.tzinfo is None:
                        # 假设是UTC时间
                        utc_tz = timezone.utc
                        dt = value.replace(tzinfo=utc_tz)
                    else:
                        dt = value
                    beijing_tz = timezone(timedelta(hours=8))
                    dt = dt.astimezone(beijing_tz)
                    return dt.strftime('%Y-%m-%d')
            except:
                return str(value)
        elif field_type == 'boolean' or field_type == 'checkbox':
            return '是' if value in ['true', 'True', True, 1, '1'] else '否'
        elif field_type == 'select':
            options = field_config.get('options', [])
            if value in options:
                return value
            return str(value)
        else:
            return str(value)
    
    def generate_form_field(self, field_config, value=''):
        """生成表单字段HTML"""
        field_name = field_config['name']
        field_label = field_config['label']
        field_type = field_config['type']
        is_required = field_config['required']
        
        required_attr = 'required' if is_required else ''
        required_label = ' *' if is_required else ''
        
        if field_type == 'text':
            return f'''
            <div class="form-group">
                <label>{field_label}{required_label}</label>
                <input type="text" name="dynamic_{field_name}" class="form-control" value="{value}" {required_attr}>
            </div>
            '''
        elif field_type == 'number':
            return f'''
            <div class="form-group">
                <label>{field_label}{required_label}</label>
                <input type="number" name="dynamic_{field_name}" class="form-control" value="{value}" {required_attr}>
            </div>
            '''
        elif field_type == 'date':
            return f'''
            <div class="form-group">
                <label>{field_label}{required_label}</label>
                <input type="date" name="dynamic_{field_name}" class="form-control" value="{value}" {required_attr}>
            </div>
            '''
        elif field_type == 'datetime':
            return f'''
            <div class="form-group">
                <label>{field_label}{required_label}</label>
                <input type="datetime-local" name="dynamic_{field_name}" class="form-control" value="{value}" {required_attr}>
            </div>
            '''
        elif field_type == 'select':
            options = field_config.get('options', [])
            options_html = ''
            for option in options:
                selected = 'selected' if option == value else ''
                options_html += f'<option value="{option}" {selected}>{option}</option>'
            
            return f'''
            <div class="form-group">
                <label>{field_label}{required_label}</label>
                <select name="dynamic_{field_name}" class="form-control" {required_attr}>
                    <option value="">请选择</option>
                    {options_html}
                </select>
            </div>
            '''
        elif field_type == 'textarea':
            return f'''
            <div class="form-group">
                <label>{field_label}{required_label}</label>
                <textarea name="dynamic_{field_name}" class="form-control" rows="3" {required_attr}>{value}</textarea>
            </div>
            '''
        elif field_type == 'boolean':
            checked = 'checked' if value in ['true', 'True', True, 1, '1'] else ''
            return f'''
            <div class="form-group">
                <div class="form-check">
                    <input type="checkbox" name="dynamic_{field_name}" class="form-check-input" {checked}>
                    <label class="form-check-label">{field_label}</label>
                </div>
            </div>
            '''
        else:
            return f'''
            <div class="form-group">
                <label>{field_label}{required_label}</label>
                <input type="text" name="dynamic_{field_name}" class="form-control" value="{value}" {required_attr}>
            </div>
            ''' 