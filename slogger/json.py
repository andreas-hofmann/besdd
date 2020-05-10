from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.utils import timezone as tz

from . import models
from . import functions
from . import mixins
from . import helpers
from . import decorators


@login_required
@decorators.only_own_children
def get_growth_data(request, child_id=None):
    def get_weeks(delta):
        return delta.days/7

    measurements, events = helpers.fetch_growth_from_db(request, child_id)
    c = models.Child.objects.get(id=child_id)

    response = {
        'age_weeks':  [],
        'weight': [],
        'height': [],
        'events': [],
    }

    cur_week = 0
    for m in measurements:
        target_week = round(c.age_weeks(m.dt.date()))

        while cur_week < target_week:
            if response['age_weeks'][-1] != cur_week:
                response['age_weeks'].append(cur_week)
                response['weight'].append(None)
                response['height'].append(None)
            cur_week += 1

        response['age_weeks'].append(cur_week)
        response['weight'].append(m.weight)
        response['height'].append(m.height)

    #totals = functions.merge_totals()

    return JsonResponse(response)

@login_required
@decorators.only_own_children
def get_percentile_data(request, child_id=None, m_type=None):
    measurements, events = helpers.fetch_growth_from_db(request, child_id)
    c = models.Child.objects.get(id=child_id)

    if m_type == "height":
        attr = "height"
        type_filter = "LH"
    elif m_type == "weight":
        attr = "weight"
        type_filter = "W"
    else:
        raise ValueError("Wrong percentile type specified: " + str(m_type))

    percentiles = models.Percentile.objects.filter(gender=c.gender).filter(m_type=type_filter).order_by('day')

    response = {
        'days':  [],
        'value': [],
        'p5': [],
        'p10': [],
        'p25': [],
        'p50': [],
        'p75': [],
        'p90': [],
        'p95': [],
    }

    cur_day = 0
    for m in measurements:
        target_day = round(c.age_days(m.dt.date()))

        while cur_day < target_day:
            if response['days'][-1] != cur_day:
                response['days'].append(cur_day)
                response['value'].append(None)
                response['p5'].append(percentiles[cur_day].p5)
                response['p10'].append(percentiles[cur_day].p10)
                response['p25'].append(percentiles[cur_day].p25)
                response['p50'].append(percentiles[cur_day].p50)
                response['p75'].append(percentiles[cur_day].p75)
                response['p90'].append(percentiles[cur_day].p90)
                response['p95'].append(percentiles[cur_day].p95)
            cur_day += 1

        response['days'].append(cur_day)
        response['value'].append(getattr(m, attr))
        response['p5'].append(percentiles[cur_day].p5)
        response['p10'].append(percentiles[cur_day].p10)
        response['p25'].append(percentiles[cur_day].p25)
        response['p50'].append(percentiles[cur_day].p50)
        response['p75'].append(percentiles[cur_day].p75)
        response['p90'].append(percentiles[cur_day].p90)
        response['p95'].append(percentiles[cur_day].p95)

    #totals = functions.merge_totals()

    return JsonResponse(response)


@login_required
@decorators.only_own_children
def get_histogram_data(request, child_id=None):

    mdfactor = request.user.usersettings.histogram_factor_md
    raster = request.user.usersettings.histogram_raster

    sleep, meal, diaper = helpers.fetch_summary_from_db(request, child_id)

    sleepdata = functions.get_hist_data(sleep, raster, raster)
    mealdata = functions.get_hist_data(meal, raster*mdfactor, raster*mdfactor)
    diaperdata = functions.get_hist_data(diaper, raster*mdfactor, raster*mdfactor)

    response = {
        'time':  [],
        'sleep': [],
        'meals': [],
        'diapers': [],
    }

    for d in sleepdata:
        response['time'] .append(d[0])
        response['sleep'].append(d[1])

    for d in mealdata:
        for i in range(mdfactor):
            response['meals'].append(d[1])

    for d in diaperdata:
        for i in range(mdfactor):
            response['diapers'].append(d[1])

    return JsonResponse(response)


@login_required
@decorators.only_own_children
def get_summary_data_list(request, child_id=None):
    sleep, meal, diaper = helpers.fetch_summary_from_db(request, child_id)
    events, diary, measurements = helpers.fetch_specials_from_db(request, child_id)

    measurements = functions.convert_to_totals(measurements, "measurements", "height", "weight")
    events = functions.convert_to_totals(events, "events", "event", "description")
    diary = functions.convert_to_totals(diary, "diary", "title", "content")

    h_day = request.user.usersettings.start_hour_day
    h_night = request.user.usersettings.start_hour_night

    sleeptotals = functions.calculate_sleep_totals(sleep, h_day, h_night)
    mealtotals = functions.calculate_totals(meal, "meals", h_day, h_night)
    diapertotals = functions.calculate_totals(diaper, "diapers", h_day, h_night)

    totals = functions.merge_totals(sleeptotals, mealtotals, diapertotals, measurements, events, diary)

    return JsonResponse([{'day': t[0], 'data': t[1]} for t in totals][::-1], safe=False)


@login_required
@decorators.only_own_children
def get_summary_data_graph(request, child_id=None):

    def sec_to_h(sec):
        return sec/3600.0

    sleep, meal, diaper = helpers.fetch_summary_from_db(request, child_id)

    h_day = request.user.usersettings.start_hour_day
    h_night = request.user.usersettings.start_hour_night

    sleeptotals = functions.calculate_sleep_totals(sleep, h_day, h_night)
    mealtotals = functions.calculate_totals(meal, "meals", h_day, h_night)
    diapertotals = functions.calculate_totals(diaper, "diapers", h_day, h_night)

    totals = functions.merge_totals(sleeptotals, mealtotals, diapertotals)

    response = {
        'day':       [],
        'sum_h':     [],
        'day_h':     [],
        'night_h':   [],
        'sum_cnt':   [],
        'day_cnt':   [],
        'night_cnt': [],
        'diapers':   [],
        'meals':     [],
    }

    for d in totals:
        response['day'].append(d[0])

        try:
            response['sum_h'].append(sec_to_h(d[1]['sum']['time']))
        except:
            response['sum_h'].append(None)
        try:
            response['day_h'].append(sec_to_h(d[1]['day']['time']))
        except:
            response['day_h'].append(None)
        try:
            response['night_h'].append(sec_to_h(d[1]['night']['time']))
        except:
            response['night_h'].append(None)
        try:
            response['sum_cnt'].append(d[1]['sum']['count'])
        except:
            response['sum_cnt'].append(None)
        try:
            response['day_cnt'].append(d[1]['day']['count'])
        except:
            response['day_cnt'].append(None)
        try:
            response['night_cnt'].append(d[1]['night']['count'])
        except:
            response['night_cnt'].append(None)
        try:
            response['diapers'].append(d[1]['diapers']['sum']['count'])
        except:
            response['diapers'].append(None)
        try:
            response['meals'].append(d[1]['meals']['sum']['count'])
        except:
            response['meals'].append(None)

    return JsonResponse(response)

@login_required
@decorators.only_own_children
def get_check(request, child_id=None):
    children = models.Child.objects.filter(parents__id=request.user.id)
    child = get_object_or_404(models.Child, id=child_id)

    response = {
        'eat':    {},
        'sleep':  {},
        'diaper': {},
    }

    try:
        s = models.SleepPhase.objects.filter(child=child_id).latest('dt')

        if s.dt and not s.dt_end:
            response['sleep']["state"] = 0
            diff = (tz.now() - s.dt)
        else:
            response['sleep']["state"] = 1
            diff = (tz.now() - s.dt_end)

        secs = diff.seconds
        days = diff.days
        response['sleep']["since_h"] = f"{int(secs/3600)}"
        response['sleep']["since_m"] = f"{int((secs%3600)/60)}"
        response['sleep']["since_d"] = f"{int(days)}"
    except Exception as e:
        response['sleep']["state"] = -1

    try:
        m = models.Meal.objects.filter(child=child_id).latest('dt')

        diff = (tz.now() - m.dt)
        secs = diff.seconds
        days = diff.days
        response['eat']["since_h"] = f"{int(secs/3600)}"
        response['eat']["since_m"] = f"{int((secs%3600)/60)}"
        response['eat']["since_d"] = f"{int(days)}"
        response['eat']["state"] = 1
    except Exception as e:
        response['eat']["state"] = -1

    try:
        d = models.Diaper.objects.filter(child=child_id).latest('dt')

        diff = (tz.now() - d.dt)
        secs = diff.seconds
        days = diff.days
        response['diaper']["since_h"] = f"{int(secs/3600)}"
        response['diaper']["since_m"] = f"{int((secs%3600)/60)}"
        response['diaper']["since_d"] = f"{int(days)}"
        response['diaper']["state"] = 1
    except Exception as e:
        response['diaper']["state"] = 0

    return JsonResponse(response)