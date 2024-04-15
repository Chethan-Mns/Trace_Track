from datetime import datetime, timedelta
from pytz import timezone
import uuid


def getDateTime():
    now_utc = datetime.now(timezone('UTC'))
    return now_utc


def utcfromtimestamp(date):
    return datetime.fromtimestamp(date, timezone('UTC'))


def getUniqueId():
    return str(uuid.uuid4())


def getCurrentTime():
    format = "%d-%m-%Y %H:%M:%S"
    now_utc = datetime.now(timezone('UTC'))
    asia_time = now_utc.astimezone(timezone('Asia/Kolkata'))
    return str(asia_time.strftime(format))


def getCurrentDateForDb():
    format = "%d-%m-%Y"
    now_utc = datetime.now(timezone('UTC'))
    asia_time = now_utc.astimezone(timezone('Asia/Kolkata'))
    return str(asia_time.strftime(format))


def calculateTimeToReach(speed, distane):
    timeFormat = "%H:%M"
    timeTaken = distane / speed
    now_utc = datetime.now(timezone('UTC'))
    asia_time = now_utc.astimezone(timezone('Asia/Kolkata'))
    caculatedTime = asia_time+timedelta(hours=timeTaken)
    return str(caculatedTime.strftime(timeFormat))
