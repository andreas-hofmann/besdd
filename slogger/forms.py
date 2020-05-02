from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from django.utils import timezone as tz

from bootstrap_datepicker_plus import DateTimePickerInput

from . import models

class GenericHelperForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.form_id = 'id-sleepphaseform'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        self.helper.form_method = 'post'

        if self.fields.get('dt'):
            self.fields['dt'].widget = DateTimePickerInput(options={'format': 'YYYY-MM-DD HH:mm',
                                                                           'collapse': False,
                                                                           'showClear': True,
                                                                           'ignoreReadonly': True,
                                                                           'showTodayButton': True})
            self.fields['dt'].widget.attrs['readonly'] = True

        self.helper.add_input(Submit('submit', 'Save'))


class SleepPhaseForm(GenericHelperForm):
    class Meta:
        fields = ('dt', 'dt_end')
        model = models.SleepPhase

    def __init__(self, *args, **kwargs):
        super(SleepPhaseForm, self).__init__(*args, **kwargs)

        self.fields['dt_end'].widget = DateTimePickerInput(options={'format': 'YYYY-MM-DD HH:mm',
                                                                     'collapse': False,
                                                                     'showClear': True,
                                                                     'ignoreReadonly': True,
                                                                     'showTodayButton': True})
        self.fields['dt_end'].widget.attrs['readonly'] = True

    def clean(self):
        dt = self.data.get('dt')
        dt_end = self.data.get('dt_end')

        if dt and dt_end:
            if dt > dt_end:
                raise forms.ValidationError("Start time must not be after end time.", code='invalid')

            if (tz.datetime.fromisoformat(dt_end) - tz.datetime.fromisoformat(dt)) > tz.timedelta(days=1):
                raise forms.ValidationError("Sleep phases > 1 day are not supported.", code='invalid')

        return super().clean()

class ChildForm(GenericHelperForm):
    class Meta:
        model = models.Child
        exclude = ['created_by', 'dt']

class MeasurementForm(GenericHelperForm):
    class Meta:
        model = models.Measurement
        exclude = ['child']

class FoodForm(GenericHelperForm):
    class Meta:
        model = models.Food
        exclude = ['is_default', 'created_by', 'dt']

class MealForm(GenericHelperForm):
    class Meta:
        model = models.Meal
        exclude = ['child', 'created_by']

    food = forms.ModelMultipleChoiceField(models.Food.objects.none())

    def __init__(self, child=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not child and kwargs['initial'].get('child'):
            child = kwargs['initial']['child']
        if not child:
            child = kwargs['instance'].child

        self.fields['food'].queryset = models.Food.objects.filter(
            created_by__in=child.parents.all()
        )

class DiaperContentForm(GenericHelperForm):
    class Meta:
        model = models.DiaperContent
        exclude = ['is_default', 'created_by', 'dt']

class DiaperForm(GenericHelperForm):
    class Meta:
        model = models.Diaper
        exclude = ['child', 'created_by']

    content = forms.ModelMultipleChoiceField(models.DiaperContent.objects.none())

    def __init__(self, child=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not child and kwargs['initial'].get('child'):
            child = kwargs['initial']['child']
        if not child:
            child = kwargs['instance'].child

        self.fields['content'].queryset = models.DiaperContent.objects.filter(
            created_by__in=child.parents.all()
        )

class EventForm(GenericHelperForm):
    class Meta:
        model = models.Event
        exclude = ['child']

class DiaryEntryForm(GenericHelperForm):
    class Meta:
        model = models.DiaryEntry
        exclude = ['child']