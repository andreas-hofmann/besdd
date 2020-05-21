from datetime import datetime, timedelta, time
from django.utils import timezone as tz
from datetime import time, date

def merge_totals(totals, *args):
    for arg in args:
        totals.extend(arg)
    totals.sort(key=lambda k: k[0])

    i = 0
    while i < len(totals):
        if i < len(totals)-1 and totals[i][0] == totals[i+1][0]:
            totals[i] = list(totals[i])
            totals[i][1] = { **totals[i][1], **totals[i+1][1] }
            totals.pop(i+1)
        else:
            i += 1

    return totals

def convert_to_totals(data, dict_key, *attributes):
    totals = {}

    for d in data:
        my_dt = tz.localtime(d.dt)
        main_key = str(my_dt.date())

        if not totals.get(main_key):
            totals[main_key] = { dict_key: [] }

        entry = {}

        for a in attributes:
            entry[a] = getattr(d, a)

        totals[main_key][dict_key].append(entry)

    return sorted(totals.items(), key=lambda kv: date.fromisoformat(kv[0]))

def calculate_average(totals, key):
    total_sleep = 0
    total_days = 0

    if type(totals) is dict:
        totals = tuple(totals.items())

    for d in totals:
        total_days += 1
        try:
            total_sleep += d[1]['sum'][key]
        except KeyError:
            pass

    try:
        return total_sleep/total_days
    except ZeroDivisionError:
        return 0

def calculate_totals(data, dict_key, h_day=8, h_night=19):
    totals = {}

    last_d = None
    for d in data:
        my_dt = tz.localtime(d.dt)
        main_key = str(my_dt.date())

        if not totals.get(main_key):
            totals[main_key] = {
            }

        if not totals[main_key].get(dict_key):
            totals[main_key][dict_key] = {
                'sum':   { "count": 0, "time": 0 },
                'day':   { "count": 0, "time": 0 },
                'night': { "count": 0, "time": 0 },
            }

        duration_secs = 0
        totals[main_key][dict_key]['sum']['count'] += 1
        if last_d:
            duration_secs = (d.dt-last_d.dt).total_seconds()
            totals[main_key][dict_key]['sum']['time'] += duration_secs

        key = 'night'
        if  my_dt.time() >= time(hour=h_day) and my_dt.time() <= time(hour=h_night):
            key = 'day'

        totals[main_key][dict_key][key]['time'] += duration_secs
        totals[main_key][dict_key][key]['count'] += 1

        last_d = d

    return sorted(totals.items(), key=lambda kv: date.fromisoformat(kv[0]))

def calculate_duration_totals(data, h_day=8, h_night=19):
    totals = {}

    carried_secs = {
        'sum' : 0,
        'daynight' : 0,
    }

    for d in data:
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

        carried_secs['sum'] = d.duration_sec_day(tomorrow=True)

        key = 'night'
        if  my_dt.time() >= time(hour=h_day) and my_dt.time() <= time(hour=h_night):
            key = 'day'

        totals[main_key][key]['time'] += carried_secs['daynight']
        totals[main_key][key]['time'] += d.duration_sec_day()
        totals[main_key][key]['count'] += 1

        carried_secs['daynight'] = d.duration_sec_day(tomorrow=True)

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
            k = tz.localtime(s).time().strftime("%H:%M")
            if not hist_data.get(k):
                hist_data[k] = 1
            else:
                hist_data[k] += 1
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
