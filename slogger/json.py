from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.utils import timezone as tz

from . import models
from . import functions
from . import mixins
from . import helpers

@login_required
def get_histogram_data(request, child_id=None, raster=10):
    sleepdata = models.SleepPhase.objects.filter(child=child_id)
    sleepdata = helpers.filter_GET_daterage(request, sleepdata)
    sleepdata = functions.get_hist_data(sleepdata, raster, raster)

    mealdata = models.Meal.objects.filter(child=child_id)
    mealdata = helpers.filter_GET_daterage(request, mealdata)
    mealdata = functions.get_hist_data(mealdata, raster, raster)

    diaperdata = models.Meal.objects.filter(child=child_id)
    diaperdata = helpers.filter_GET_daterage(request, diaperdata)
    diaperdata = functions.get_hist_data(diaperdata, raster, raster)

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
        response['meals'].append(d[1])

    for d in diaperdata:
        response['diapers'].append(d[1])

    return JsonResponse(response)

@login_required
def get_summary_data(request, child_id=None):

    def sec_to_h(sec):
        return sec/3600.0

    data = models.SleepPhase.objects.filter(child=child_id)
    data = helpers.filter_GET_daterage(request, data)
    totals = functions.calculate_sleep_totals(data)

    response = {
        'day':       [],
        'sum_h':     [],
        'day_h':     [],
        'night_h':   [],
        'sum_cnt':   [],
        'day_cnt':   [],
        'night_cnt': [],
    }

    for d in totals:
        response['day']      .append(d[0])
        response['sum_h']    .append(sec_to_h(d[1]['sum']['time']))
        response['day_h']    .append(sec_to_h(d[1]['day']['time']))
        response['night_h']  .append(sec_to_h(d[1]['night']['time']))
        response['sum_cnt']  .append(         d[1]['sum']['count'])
        response['day_cnt']  .append(         d[1]['day']['count'])
        response['night_cnt'].append(         d[1]['night']['count'])

    return JsonResponse(response)

@login_required
def get_check(request, child_id=None):
    children = models.Child.objects.filter(parents__id=request.user.id)
    child = get_object_or_404(models.Child, id=child_id)

    if child not in children:
        raise PermissionDenied("Invalid child requested")

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