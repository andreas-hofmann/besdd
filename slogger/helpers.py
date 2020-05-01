from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils import timezone as tz

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
