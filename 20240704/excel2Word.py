from docx import Document
from docx.shared import Pt
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ROW_HEIGHT_RULE
import os

import pandas as pd
from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt

# ... 其他代码 ...
work_dir = 'D:\\1'
excel_files = [f for f in os.listdir(
    work_dir) if f.endswith(('.xlsx', '.xls'))]

# 创建一个新的Word文档
doc = Document()
# 遍历所有Excel文件
for excel_file in excel_files:
    # ... 读取Excel文件并创建Word表格的代码 ...
    excel_path = os.path.join(work_dir, excel_file)
    # 读取Excel文件
    df = pd.read_excel(excel_path)
    # 将DataFrame转换为Word表格
    for _, row in df.iterrows():
        table = doc.add_table(rows=1, cols=len(row), style='Table Grid')
        # 添加行并设置单元格数据
        for i, value in enumerate(row):
            cell = table.cell(0, i)
            cell.text = str(value)
            # cell.vertical_alignment = 'center'  # 垂直居中对齐

    # 设置表格样式
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # 设置行高
    for row in table.rows:
        row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
        row.height = Pt(20)

# 保存Word文档
# ... 保存文档的代码 ...
output_path = os.path.join(work_dir, 'CombinedTables.docx')
doc.save(output_path)
print(f"Word文档已保存至：{output_path}")