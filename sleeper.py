import datetime
import time


# Fonction pour donner le temps de reprise en general puis dormir
def sleep_please(days=0, hours=0, minutes=0, seconds=0):
    now = datetime.datetime.now().replace(microsecond=0)
    totaltimetosleep = days*24*3600 + hours*3600 + minutes*60 + seconds
    nowdecale = now + datetime.timedelta(seconds=totaltimetosleep)
    print(f'Will finish sleep at {nowdecale.time()} ({nowdecale.date()})')
    time.sleep(totaltimetosleep)


