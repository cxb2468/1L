from apscheduler.schedulers.blocking import BlockingScheduler
import datetime


schedudler = BlockingScheduler()

# 定义一个job类，完成想要做的事
def worker():
    print("hello scheduler "+ str(datetime.datetime.now()))

# 定时每天 17:19:07秒执行任务
schedudler.add_job(worker,'cron',day_of_week ='0-6',hour = 13,minute = 46,second = 40)

schedudler.start() # 开始任务