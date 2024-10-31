import configparser

# 创建 ConfigParser 对象
config = configparser.ConfigParser()

# 添加 [hkconfig] 节
config.add_section('hkconfig')

# 设置配置项
config.set('hkconfig', 'listPath', 'path/to/your/list/file.txt')  # 设备列表文件
config.set('hkconfig', 'picPath', 'path/to/your/pic/folder/')     # 截图保存路径(末尾需加/)
config.set('hkconfig', 'pdfPath', 'path/to/your/pdf/folder/')     # PDF保存路径(末尾需加/)
config.set('hkconfig', 'reportPath', 'path/to/your/report/folder/')  # 报表保存路径(末尾需加/)
config.set('hkconfig', 'copy', 'Your Company Name')               # 公司名称
config.set('hkconfig', 'author', 'Your Name')                     # 联系人
config.set('hkconfig', 'phone', 'Your Phone Number')              # 联系电话
config.set('hkconfig', 'addr', 'Your Address')                    # 地址
config.set('hkconfig', 'customer', 'Customer Name')               # 客户名

# 写入配置文件
with open('config.ini', 'w', encoding='utf-8') as configfile:
    config.write(configfile)

print("配置文件已生成")
