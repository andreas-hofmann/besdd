from django.core.exceptions import ValidationError, ObjectDoesNotExist
from datetime import datetime
from django.utils import timezone as tz

from . import models


def filter_GET_daterage(request, data):
    date_from = request.GET.get("from")
    date_to = request.GET.get("to")

    if date_from and date_to:
        try:
            date_from = tz.make_aware(datetime.strptime(date_from, "%Y-%m-%d"))
            date_to   = tz.make_aware(datetime.strptime(date_to,   "%Y-%m-%d"))
        except ValueError:
            raise ValidationError("Invalid date supplied.")

        data = data.filter(dt__range=[date_from, date_to])

    return data


def fetch_growth_from_db(request, child_id):
    measurements = models.Measurement.objects.filter(child=child_id).order_by("dt")
    measurements = filter_GET_daterage(request, measurements)

    events = models.Event.objects.filter(child=child_id).order_by("dt")
    events = filter_GET_daterage(request, events)

    return measurements, events


def fetch_summary_from_db(request, child_id):
    sleep = models.SleepPhase.objects.filter(child=child_id).order_by("dt")
    sleep = filter_GET_daterage(request, sleep)

    meal = models.Meal.objects.filter(child=child_id).order_by("dt")
    meal = filter_GET_daterage(request, meal)

    diaper = models.Diaper.objects.filter(child=child_id).order_by("dt")
    diaper = filter_GET_daterage(request, diaper)

    return sleep, meal, diaper


def  fetch_specials_from_db(request, child_id):
    events = models.Event.objects.filter(child=child_id).order_by("dt")
    events = filter_GET_daterage(request, events)

    diary = models.DiaryEntry.objects.filter(child=child_id).order_by("dt")
    diary = filter_GET_daterage(request, diary)

    measurements = models.Measurement.objects.filter(child=child_id).order_by("dt")
    measurements = filter_GET_daterage(request, measurements)

    return events, diary, measurements


def get_user_settings(user):
    try:
        s = models.UserSettings.objects.get(user=user)
    except ObjectDoesNotExist:
        s = models.UserSettings(user=user)
        s.save()

    return s