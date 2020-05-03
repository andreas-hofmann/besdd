from django.contrib import admin

from .models import *

admin.site.register(UserSettings)
admin.site.register(Child)
admin.site.register(SleepPhase)
admin.site.register(Measurement)
admin.site.register(Food)
admin.site.register(Meal)
admin.site.register(Diaper)
admin.site.register(DiaperContent)
admin.site.register(Event)
admin.site.register(DiaryEntry)