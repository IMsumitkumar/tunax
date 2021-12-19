
from django.utils.timezone import make_aware

def combine_datetime(date, time):
    import datetime
    dt = datetime.datetime(int(date[0:4]), int(date[5:7]), int(date[8:10]))
    tm = datetime.time(int(time[0:2]), int(time[3:5]))
    combined = dt.combine(dt, tm)
    aware_datetime = make_aware(combined)
    return aware_datetime

