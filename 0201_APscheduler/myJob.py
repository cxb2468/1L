# coding:utf-8
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor


def my_job(id='my_job'):
    print(id, '-->', datetime.datetime.now())


jobstores = {
    'default': MemoryJobStore()

}
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(10)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}
scheduler = BlockingScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
scheduler.add_job(my_job, args=['job_interval', ], id='job_interval', trigger='interval', seconds=5, replace_existing=True)
scheduler.add_job(my_job, args=['job_cron', ], id='job_cron', trigger='cron', month='1-8,11-12', hour='7-11',second='*/10',end_date='2020-05-30')
scheduler.add_job(my_job, args=['job_once_now', ], id='job_once_now')
scheduler.add_job(my_job, args=['job_date_once', ], id='job_date_once', trigger='date', run_date='2021-02-05 07:48:05')
try:
    scheduler.start()
except SystemExit:
    print('exit')
    exit()
