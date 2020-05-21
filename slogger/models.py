from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from django.utils import timezone as tz

from .mixins import AttributeModelMixin, DurationModelMixin

class UserSettings(models.Model,
                   AttributeModelMixin):

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)

    paginate_by = models.IntegerField("Paginate by", default=20)
    date_range_days = models.IntegerField("Default summary date range", default=14)

    sleep_enabled = models.BooleanField("Draw sleep data in graph by default", default=True);
    meals_enabled = models.BooleanField("Draw meal data in graph by default", default=False);
    diapers_enabled = models.BooleanField("Draw diaper data in graph by default", default=False);

    default_child = models.ForeignKey("Child", null=True, blank=True, on_delete=models.CASCADE)

    start_hour_day = models.IntegerField("Day starts at (h)", default=8)
    start_hour_night = models.IntegerField("night starts at (h)", default=19)

    histogram_raster = models.IntegerField("Time raster for histogram (minutes)", default=10)
    histogram_factor_md = models.IntegerField("Time factor for meals+diapers in histogram", default=6)

    def __str__(self):
        return f"Settings for { self.user }"


@receiver(signals.post_save, sender=get_user_model())
def default_settings(sender, instance, created, **kwargs):
    try:
        UserSettings.objects.get(user=instance)
    except ObjectDoesNotExist:
        defaults = UserSettings(user=instance)
        defaults.save()


class Child(models.Model,
            AttributeModelMixin):

    GENDER_CHOICES=[
        ("M", "Male"),
        ("F", "Female"),
    ]

    created_by = models.ForeignKey(get_user_model(), related_name="created_by", on_delete=models.CASCADE)
    dt = models.DateTimeField("Created on", default=tz.now)
    parents = models.ManyToManyField(get_user_model())
    name = models.CharField(max_length=100)
    birthday = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    def __str__(self):
        return self.name

    def age_days(self, date=None):
        if not date:
            date = tz.localtime().date()
        if type(date) == str:
            date = tz.datetime.fromisoformat(date).date()
        return (date-self.birthday).days

    def age_weeks(self, date=None):
        return self.age_days(date) / 7

class SleepPhase(models.Model,
                 DurationModelMixin,
                 AttributeModelMixin):

    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    dt = models.DateTimeField("Start", default=tz.now)
    dt_end = models.DateTimeField("End", null=True, blank=True)

    def add(self, child=None, dt=None, dt_end=None):
        self.child = child
        self.dt = dt
        self.dt_end = dt_end

    def __str__(self):
        try:
            return "%s - %s: From %s to %s. Duration: %s." % \
                (self.child.name, self.dt.date(), self.dt.time(), self.dt_end.time(), self.duration_hhmm())
        except AttributeError:
            return "%s - %s: From %s." % \
                (self.child.name, self.dt.date(), self.dt.time())


class Measurement(models.Model,
                  AttributeModelMixin):

    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    dt = models.DateTimeField("Date taken", default=tz.now)
    weight = models.FloatField("Weight (kg)", null=True, blank=True)
    height = models.FloatField("Height (cm)", null=True, blank=True)

    def __str__(self):
        return str(self.child.name) + " - " + \
               str(tz.localdate(self.dt)) + " - Weight: " + str(self.weight) \
                                          + ", height: " + str(self.height)


class Food(models.Model,
          AttributeModelMixin):

    is_default = models.BooleanField(default=False)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    dt = models.DateTimeField("Created", default=tz.now)
    name = models.CharField("Name", max_length=100)
    description = models.TextField("Description", max_length=2000, null=True, blank=True)

    def __str__(self):
        return self.name


class Meal(models.Model,
           DurationModelMixin,
           AttributeModelMixin):

    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    dt = models.DateTimeField("Eaten on", default=tz.now)
    food = models.ManyToManyField(Food)
    dt_end = models.DateTimeField("Eaten until", default=None, null=True, blank=True)

    def __str__(self):
        return str(self.child.name) + " - " + str(tz.localtime(self.dt))


class DiaperContent(models.Model,
                    AttributeModelMixin):

    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    is_default = models.BooleanField(default=False)
    dt = models.DateTimeField("Created", default=tz.now)
    name = models.CharField("Name", max_length=100)
    description = models.TextField("Description", max_length=2000, null=True, blank=True)

    def __str__(self):
        return self.name


class Diaper(models.Model,
             AttributeModelMixin):

    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    dt = models.DateTimeField("Changed on", default=tz.now)
    content = models.ManyToManyField(DiaperContent, blank=True)

    def __str__(self):
        return str(self.child.name) + " - " + \
               str(tz.localtime(self.dt).date()) + " " + \
               str(tz.localtime(self.dt).time())  + " " + \
               "+".join([str(d) for d in self.content.all()])


class Event(models.Model,
            AttributeModelMixin):

    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    dt = models.DateTimeField("Occured on", default=tz.now)
    event = models.CharField("Name", max_length=100)
    description = models.TextField("Description", max_length=2000, null=True, blank=True)

    def __str__(self):
        return str(self.child.name) + " - " + \
               str(tz.localdate(self.dt)) + " " + self.event

class DiaryEntry(models.Model,
                 AttributeModelMixin):

    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    dt = models.DateTimeField("Date", default=tz.now)
    title = models.CharField("Title", max_length=100)
    content = models.TextField("Entry")

    def __str__(self):
        return str(self.child.name) + " - " + \
               str(tz.localdate(self.dt)) + " " + self.title

class Percentile(models.Model):
    GENDER_CHOICES=[
        ("M", "Male"),
        ("F", "Female"),
    ]
    MEAS_CHOICES=[
        ("L", "Length/Height"),
        ("W", "Weight"),
    ]

    dt = models.DateTimeField("Added on", default=tz.now)

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    m_type = models.CharField(max_length=1, choices=MEAS_CHOICES)
    day = models.IntegerField()

    p01 = models.FloatField()
    p1 = models.FloatField()
    p3 = models.FloatField()
    p5 = models.FloatField()
    p10 = models.FloatField()
    p15 = models.FloatField()
    p25 = models.FloatField()
    p50 = models.FloatField()
    p75 = models.FloatField()
    p85 = models.FloatField()
    p90 = models.FloatField()
    p95 = models.FloatField()
    p97 = models.FloatField()
    p99 = models.FloatField()
    p999 = models.FloatField()