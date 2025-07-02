# 字段配置文件
# 用于灵活管理各模块的字段显示、验证、导入导出等

FIELD_CONFIG = {
    'contract': {
        'fields': [
            {
                'name': 'name',
                'label': '合同名称',
                'type': 'text',
                'required': True,
                'searchable': True,
                'exportable': True,
                'importable': True,
                'width': 150,
                'order': 1
            },
            {
                'name': 'party_a',
                'label': '甲方',
                'type': 'text',
                'required': False,
                'searchable': True,
                'exportable': True,
                'importable': True,
                'width': 120,
                'order': 2
            },
            {
                'name': 'party_b',
                'label': '乙方',
                'type': 'text',
                'required': False,
                'searchable': True,
                'exportable': True,
                'importable': True,
                'width': 120,
                'order': 3
            },
            {
                'name': 'number',
                'label': '合同编号',
                'type': 'text',
                'required': False,
                'searchable': True,
                'exportable': True,
                'importable': True,
                'width': 120,
                'order': 4
            },
            {
                'name': 'amount',
                'label': '合同金额',
                'type': 'number',
                'required': False,
                'searchable': False,
                'exportable': True,
                'importable': True,
                'width': 100,
                'order': 5
            },
            {
                'name': 'sign_date',
                'label': '签订日期',
                'type': 'date',
                'required': False,
                'searchable': False,
                'exportable': True,
                'importable': True,
                'width': 100,
                'order': 6
            },
            {
                'name': 'manager',
                'label': '负责人',
                'type': 'text',
                'required': False,
                'searchable': True,
                'exportable': True,
                'importable': True,
                'width': 100,
                'order': 7
            },
            {
                'name': 'status',
                'label': '状态',
                'type': 'select',
                'options': ['进行中', '已完成', '已终止', '待审核'],
                'required': False,
                'searchable': True,
                'exportable': True,
                'importable': True,
                'width': 80,
                'order': 8
            },
            {
                'name': 'remark',
                'label': '备注',
                'type': 'textarea',
                'required': False,
                'searchable': False,
                'exportable': True,
                'importable': True,
                'width': 200,
                'order': 9
            },
            {
                'name': 'attachment',
                'label': '附件',
                'type': 'file',
                'required': False,
                'searchable': False,
                'exportable': False,
                'importable': False,
                'width': 100,
                'order': 10
            },
            {
                'name': 'modified_by',
                'label': '修改人',
                'type': 'text',
                'required': False,
                'searchable': False,
                'exportable': True,
                'importable': False,
                'width': 100,
                'order': 11
            },
            {
                'name': 'modified_at',
                'label': '修改时间',
                'type': 'datetime',
                'required': False,
                'searchable': False,
                'exportable': True,
                'importable': False,
                'width': 150,
                'order': 12
            }
        ],
        'table_config': {
            'page_size_options': [10, 20, 50, 100],
            'default_page_size': 20,
            'sortable': True,
            'exportable': True,
            'importable': True
        }
    },
    
    'project': {
        'fields': [
            {
                'name': 'name',
                'label': '项目名称',
                'type': 'text',
                'required': True,
                'searchable': True,
                'exportable': True,
                'importable': True,
                'width': 150,
                'order': 1
            },
            {
                'name': 'owner',
                'label': '业主单位',
                'type': 'text',
                'required': False,
                'searchable': True,
                'exportable': True,
                'importable': True,
                'width': 150,
                'order': 2
            },
            {
                'name': 'address',
                'label': '地址',
                'type': 'text',
                'required': False,
                'searchable': True,
                'exportable': True,
                'importable': True,
                'width': 200,
                'order': 3
            },
            {
                'name': 'contact',
                'label': '联系人',
                'type': 'text',
                'required': False,
                'searchable': True,
                'exportable': True,
                'importable': True,
                'width': 100,
                'order': 4
            },
            {
                'name': 'phone',
                'label': '电话',
                'type': 'text',
                'required': False,
                'searchable': True,
                'exportable': True,
                'importable': True,
                'width': 120,
                'order': 5
            },
            {
                'name': 'remark',
                'label': '备注',
                'type': 'textarea',
                'required': False,
                'searchable': False,
                'exportable': True,
                'importable': True,
                'width': 200,
                'order': 6
            },
            {
                'name': 'modified_by',
                'label': '修改人',
                'type': 'text',
                'required': False,
                'searchable': False,
                'exportable': True,
                'importable': False,
                'width': 100,
                'order': 7
            },
            {
                'name': 'modified_at',
                'label': '修改时间',
                'type': 'datetime',
                'required': False,
                'searchable': False,
                'exportable': True,
                'importable': False,
                'width': 150,
                'order': 8
            }
        ],
        'table_config': {
            'page_size_options': [10, 20, 50, 100],
            'default_page_size': 20,
            'sortable': True,
            'exportable': True,
            'importable': True
        }
    },
    
    'staff': {
        'fields': [
            {
                'name': 'name',
                'label': '姓名',
                'type': 'text',
                'required': True,
                'searchable': True,
                'exportable': True,
                'importable': True,
                'width': 100,
                'order': 1
            },
            {
                'name': 'gender',
                'label': '性别',
                'type': 'select',
                'options': ['男', '女'],
                'required': False,
                'searchable': True,
                'exportable': True,
                'importable': True,
                'width': 60,
                'order': 2
            },
            {
                'name': 'id_number',
                'label': '身份证号',
                'type': 'text',
                'required': False,
                'searchable': True,
                'exportable': True,
                'importable': True,
                'width': 150,
                'order': 3
            },
            {
                'name': 'phone',
                'label': '手机号',
                'type': 'text',
                'required': False,
                'searchable': True,
                'exportable': True,
                'importable': True,
                'width': 120,
                'order': 4
            },
            {
                'name': 'bank_number',
                'label': '银行卡号',
                'type': 'text',
                'required': False,
                'searchable': True,
                'exportable': True,
                'importable': True,
                'width': 150,
                'order': 5
            },
            {
                'name': 'bank_name',
                'label': '开户行',
                'type': 'text',
                'required': False,
                'searchable': True,
                'exportable': True,
                'importable': True,
                'width': 120,
                'order': 6
            },
            {
                'name': 'staff_type',
                'label': '员工类别',
                'type': 'select',
                'options': ['正式员工', '临时工', '实习生', '外包人员'],
                'required': False,
                'searchable': True,
                'exportable': True,
                'importable': True,
                'width': 100,
                'order': 7
            },
            {
                'name': 'remark',
                'label': '备注',
                'type': 'textarea',
                'required': False,
                'searchable': False,
                'exportable': True,
                'importable': True,
                'width': 200,
                'order': 8
            },
            {
                'name': 'modified_by',
                'label': '修改人',
                'type': 'text',
                'required': False,
                'searchable': False,
                'exportable': True,
                'importable': False,
                'width': 100,
                'order': 9
            },
            {
                'name': 'modified_at',
                'label': '修改时间',
                'type': 'datetime',
                'required': False,
                'searchable': False,
                'exportable': True,
                'importable': False,
                'width': 150,
                'order': 10
            }
        ],
        'table_config': {
            'page_size_options': [10, 20, 50, 100],
            'default_page_size': 20,
            'sortable': True,
            'exportable': True,
            'importable': True
        }
    }
}

def get_field_config(module_name):
    """获取指定模块的字段配置"""
    return FIELD_CONFIG.get(module_name, {})

def get_visible_fields(module_name):
    """获取指定模块的可见字段（用于表格显示）"""
    config = get_field_config(module_name)
    fields = config.get('fields', [])
    # 按order排序，过滤掉不显示的字段
    return sorted([f for f in fields if f.get('exportable', True)], key=lambda x: x['order'])

def get_searchable_fields(module_name):
    """获取指定模块的可搜索字段"""
    config = get_field_config(module_name)
    fields = config.get('fields', [])
    return [f for f in fields if f.get('searchable', False)]

def get_importable_fields(module_name):
    """获取指定模块的可导入字段"""
    config = get_field_config(module_name)
    fields = config.get('fields', [])
    return [f for f in fields if f.get('importable', False)]

def get_exportable_fields(module_name):
    """获取指定模块的可导出字段"""
    config = get_field_config(module_name)
    fields = config.get('fields', [])
    return [f for f in fields if f.get('exportable', False)] 