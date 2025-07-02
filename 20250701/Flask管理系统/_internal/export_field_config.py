from app import app
from models import FieldConfig
import json

with app.app_context():
    fields = FieldConfig.query.order_by(FieldConfig.module_name, FieldConfig.field_order).all()
    preset_fields = []
    for f in fields:
        preset_fields.append({
            'module_name': f.module_name,
            'field_name': f.field_name,
            'field_label': f.field_label,
            'field_type': f.field_type,
            'is_required': f.is_required,
            'is_searchable': f.is_searchable,
            'is_exportable': f.is_exportable,
            'is_importable': f.is_importable,
            'is_visible': f.is_visible,
            'field_width': f.field_width,
            'field_order': f.field_order,
            'field_options': f.field_options or '',
            'validation_rules': f.validation_rules or ''
        })
    print(json.dumps(preset_fields, ensure_ascii=False, indent=4)) 