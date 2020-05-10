from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import *

class UserSettingsInline(admin.StackedInline):
    model = UserSettings

class UserAdmin(BaseUserAdmin):
    inlines = (UserSettingsInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

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
admin.site.register(Percentile)