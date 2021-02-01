from datetime import datetime
import os
from apscheduler.schedulers.blocking import BlockingScheduler

def tick():
    print("Tick! time is : "+ str(datetime.now()))
    print("Tick! time is : %s" % datetime.now())
    print()



if __name__ == "__main__":
    sch = BlockingScheduler()
    sch.add_job(tick,"interval",seconds=3)
    print("Ctrl+0  to exit".format(("Break" if os.name == "nt" else "C  ")))

    try:
        sch.start()
    except (KeyboardInterrupt,SystemExit):
        pass
