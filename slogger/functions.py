from datetime import datetime, timedelta, time
from django.utils import timezone as tz
from datetime import time, date

def calculate_average(totals, key):
    total_sleep = 0
    total_days = 0

    if type(totals) is dict:
        totals = tuple(totals.items())

    for d in totals:
        total_days += 1
        total_sleep += d[1]['sum'][key]

    return total_sleep/total_days

def calculate_totals(data, h_day=8, h_night=19):
    totals = {}

    for d in data:
        my_dt = tz.localtime(d.dt)
        main_key = str(my_dt.date())

        if not totals.get(main_key):
            totals[main_key] = 0

        totals[main_key] += 1

    return sorted(totals.items(), key=lambda kv: date.fromisoformat(kv[0]))

def calculate_sleep_totals(data, h_day=8, h_night=19):
    totals = {}

    for d in data:
        carried_secs = {
            'sum' : 0,
            'day' : 0,
            'night' : 0,
        }

        my_dt = tz.localtime(d.dt)
        main_key = str(my_dt.date())
        if not totals.get(main_key):
            totals[main_key] = {
                'sum':   {'time': 0, 'count': 0},
                'day':   {'time': 0, 'count': 0},
                'night': {'time': 0, 'count': 0},
            }

        totals[main_key]['sum']['time'] += carried_secs['sum']
        totals[main_key]['sum']['time'] += d.duration_sec_day()
        totals[main_key]['sum']['count'] += 1

        carried_secs['sum'] += d.duration_sec_day(tomorrow=True)

        key = 'night'
        if  my_dt.time() >= time(hour=h_day) and my_dt.time() <= time(hour=h_night):
            key = 'day'

        totals[main_key][key]['time'] += carried_secs[key]
        totals[main_key][key]['time'] += d.duration_sec_day()
        totals[main_key][key]['count'] += 1

        carried_secs[key] += d.duration_sec_day(tomorrow=True)

    return sorted(totals.items(), key=lambda kv: date.fromisoformat(kv[0]))

def get_hist_data(data, raster, resolution):
    hist_data = {}
    my_delta = timedelta(minutes=raster)

    hist_start = tz.make_aware(tz.datetime(2000, 1, 1))
    hist_end = hist_start + timedelta(days=1)

    while hist_start <= hist_end:
        time_str = tz.localtime(hist_start).time().strftime("%H:%M")
        hist_data[time_str] = 0
        hist_start += my_delta

    for d in data:
        s = d.dt.replace(second=0, microsecond=0)

        while (s.minute % raster) != 0:
            s -= timedelta(minutes=1)

        try:
            e = d.dt_end.replace(second=0, microsecond=0)
        except AttributeError:
            # We have no end date. Just increase a single time and go on.
            hist_data[tz.localtime(s).time().strftime("%H:%M")] += 1
            continue

        while (e.minute % raster) != 0:
            e += timedelta(minutes=1)

        while s <= e:
            time_str = tz.localtime(s).time().strftime("%H:%M")

            if not hist_data.get(time_str):
                hist_data[time_str] = 0

            if d.time_in_range(s):
                hist_data[time_str] += 1

            s += my_delta
    
    return sorted(hist_data.items(), key=lambda kv: time.fromisoformat(kv[0]))
