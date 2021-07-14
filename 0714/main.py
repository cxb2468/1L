import y_functions2 as yf2
from settings import Settings

y_settings = Settings()
# 导入准备模板
t_start, t_end, n = yf2.begin()
# n为计划刷御魂次数，通过begin函数输入
for k in range(n):
    print('开始刷第{}次御魂'.format(k + 1))

    # 检测挑战模板
    yf2.matchT(t_start, y_settings.start_x, y_settings.start_y)

    # 等待战斗最后结尾点三下跳过动画
    yf2.endclick(y_settings)
    print('结尾点击三次')

    # 检测结束模板
    yf2.matchT(t_end, y_settings.end_x, y_settings.end_y)

print('一共刷完了{}次御魂'.format(n))

