from django.views.generic import (
    TemplateView, ListView, CreateView, FormView, UpdateView, DeleteView, DetailView
)

from django.contrib.auth import get_user_model, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import timezone as tz

from . import models
from . import forms
from . import functions
from . import mixins
from . import helpers
from . import decorators

# Free for all views

class IndexView(mixins.AddChildContextViewMixin,
                TemplateView):
    template_name = "slogger/index.html"

    def render_to_response(self, context, **response_kwargs):
        if self.request.user.is_authenticated:
            children = models.Child.objects.filter(parents__id=self.request.user.id)
            s = helpers.get_user_settings(self.request.user)

            if s.default_child:
                return redirect('child', child_id=s.default_child.id)

            if children:
                return redirect('child', child_id=children.reverse()[0].id)
            else:
                return redirect('child_add')
        return super().render_to_response(context, **response_kwargs)

# Views requiring login

# Shortcut for adding sleepphase
@login_required
@decorators.only_own_children
def quick_add_sleepphase(request, child_id=None):
    sp = models.SleepPhase.objects.filter(child=child_id).last()

    if not sp or (sp.dt and sp.dt_end):
        return redirect('sleepphases_add', child_id=child_id)

    return redirect('sleepphases_edit', child_id=child_id, pk=sp.id)

# Template views

class SummaryPlotView(LoginRequiredMixin,
                      mixins.AddChildContextViewMixin,
                      TemplateView):
    template_name = "slogger/plots/summary.html"

# Model views

class SleepPhaseListView(LoginRequiredMixin,
                         mixins.AddChildContextViewMixin,
                         ListView):
    model = models.SleepPhase
    paginate_by = 20

    def get_queryset(self, **kwargs):
        return models.SleepPhase.objects.filter(child=self.kwargs.get('child_id')).order_by("-dt")

class SleepPhaseCreateView(LoginRequiredMixin,
                           SuccessMessageMixin,
                           mixins.AddChildContextViewMixin,
                           mixins.SetChildIdFormMixin,
                           mixins.CreatedByFormMixin,
                           CreateView):
    model = models.SleepPhase
    template_name = "generic_form.html"
    success_message = "Sleepphase added."
    form_class = forms.SleepPhaseForm

    def get_initial(self):
        initial = super().get_initial()
        if not initial.get('dt'):
            initial['dt'] = tz.now()
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Create Sleepphase"
        return ctx

    def get_success_url(self):
        return reverse_lazy('sleepphases', kwargs = {'child_id': self.object.child.id})

class SleepPhaseUpdateView(LoginRequiredMixin,
                           SuccessMessageMixin,
                           mixins.AddChildContextViewMixin,
                           UpdateView):
    model = models.SleepPhase
    template_name = "generic_form.html"
    success_message = "Sleepphase updated."
    form_class = forms.SleepPhaseForm

    def get_initial(self):
        initial = super().get_initial()
        if not initial.get('dt_end'):
            initial['dt_end'] = tz.now()
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Update Sleepphase"
        return ctx
    
    def get_success_url(self):
        return reverse_lazy('sleepphases', kwargs = {'child_id': self.object.child.id})

class SleepPhaseDeleteView(LoginRequiredMixin,
                           SuccessMessageMixin,
                           mixins.AddChildContextViewMixin,
                           DeleteView):
    model = models.SleepPhase
    template_name = "generic_delete.html"
    success_message = "Sleepphase deleted."

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Delete Sleepphase"
        ctx["delete_object_msg"] = str(models.SleepPhase.objects.get(id=self.kwargs['pk']))
        return ctx
    
    def get_success_url(self):
        return reverse_lazy('sleepphases', kwargs = {'child_id': self.object.child.id})


class ChildView(LoginRequiredMixin,
                mixins.AddChildContextViewMixin,
                DetailView):
    model = models.Child
    pk_url_kwarg = "child_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["parents"] = [ p for p in get_user_model().objects.all() if p in self.object.parents.all() ]
        return context

class ChildCreateView(LoginRequiredMixin,
                      mixins.AddChildContextViewMixin,
                      mixins.CreatedByFormMixin,
                      CreateView):
    model = models.Child
    template_name ="generic_form.html"
    success_message = "Child created."
    form_class = forms.ChildForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Add child"
        return ctx
    
    def get_success_url(self):
        return reverse_lazy('children')

class ChildUpdateView(LoginRequiredMixin,
                      mixins.AddChildContextViewMixin,
                      UpdateView):
    model = models.Child
    pk_url_kwarg = "child_id"
    template_name ="generic_form.html"
    success_message = "Child details updated."
    form_class = forms.ChildForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        if ctx['child'].created_by != ctx['view'].request.user:
            raise PermissionDenied("Ediding is only allowed for user's created children")

        ctx["headline"] = "Edit child details"
        return ctx

    def get_success_url(self):
        return reverse_lazy('child', kwargs = {'child_id': self.kwargs['child_id']})

class ChildListView(LoginRequiredMixin,
                    mixins.AddChildContextViewMixin,
                    ListView):
    def get_queryset(self):
        return models.Child.objects.filter(parents__id=self.request.user.id)


class SummaryListView(LoginRequiredMixin,
                      mixins.AddChildContextViewMixin,
                      ListView):
    template_name = "slogger/summary.html"
    paginate_by = 10

    def get_queryset(self, **kwargs):
        data = models.SleepPhase.objects.filter(child=self.kwargs.get('child_id'))
        self.totals = functions.calculate_sleep_totals(data)[::-1]
        return self.totals

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        totals = self.totals

        paginator = Paginator(totals, self.paginate_by)
        totals = paginator.get_page(context['page_obj'].number)

        context["totals"] = totals
        context["avg_sleep"] = functions.calculate_average(totals, "time")
        context["avg_phases"] = functions.calculate_average(totals, "count")

        return context


class MeasurementListView(LoginRequiredMixin,
                          mixins.AddChildContextViewMixin,
                          ListView):
    model = models.Measurement
    pk_url_kwarg = "child_id"
    paginate_by = 20

    def get_queryset(self, **kwargs):
        return models.Measurement.objects.filter(child=self.kwargs.get('child_id')).order_by("-dt")

class MeasurementCreateView(LoginRequiredMixin,
                            mixins.AddChildContextViewMixin,
                            mixins.SetChildIdFormMixin,
                            mixins.CreatedByFormMixin,
                            CreateView):
    model = models.Measurement
    template_name ="generic_form.html"
    pk_url_kwarg = "child_id"
    success_message = "Measurement added."
    form_class = forms.MeasurementForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Add measurement"
        return ctx

    def get_success_url(self):
        return reverse_lazy('measurements', kwargs = {'child_id': self.kwargs['child_id']})

class MeasurementUpdateView(LoginRequiredMixin,
                            mixins.CheckObjectChildRelationMixin,
                            UpdateView):
    model = models.Measurement
    template_name ="generic_form.html"
    success_message = "Measurement details updated."
    form_class = forms.MeasurementForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Edit measurement details"
        return ctx

    def get_success_url(self):
        return reverse_lazy('measurements', kwargs = {'child_id': self.kwargs['child_id']})

class MeasurementDeleteView(LoginRequiredMixin,
                            mixins.CheckObjectChildRelationMixin,
                            DeleteView):
    model = models.Measurement
    template_name ="generic_delete.html"
    success_message = "Measurement details deleted."

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Delete measurement?"
        ctx["delete_object_msg"] = str(models.Measurement.objects.get(id=self.kwargs['pk']))
        return ctx

    def get_success_url(self):
        return reverse_lazy('measurements', kwargs = {'child_id': self.kwargs['child_id']})

class FoodListView(LoginRequiredMixin,
                   mixins.AddChildContextViewMixin,
                   ListView):
    model = models.Food
    template_name ="generic_list.html"
    pk_url_kwarg = "child_id"
    paginate_by = 20

    def get_queryset(self, **kwargs):
        return models.Food.objects.filter(created_by=self.request.user.id).order_by("-dt")

class FoodCreateView(LoginRequiredMixin,
                     mixins.AddChildContextViewMixin,
                     mixins.CreatedByFormMixin,
                     CreateView):
    model = models.Food
    template_name ="generic_form.html"
    success_message = "Food added."
    form_class = forms.FoodForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Add Food"
        return ctx

    def get_success_url(self):
        return reverse_lazy('foods')

class FoodUpdateView(LoginRequiredMixin,
                     mixins.AddChildContextViewMixin,
                     UpdateView):
    model = models.Food
    template_name ="generic_form.html"
    success_message = "Food details updated."
    form_class = forms.FoodForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Edit food details"
        return ctx

    def get_success_url(self):
        return reverse_lazy('foods')


class MealListView(LoginRequiredMixin,
                   mixins.AddChildContextViewMixin,
                   ListView):
    model = models.Meal
    pk_url_kwarg = "child_id"
    paginate_by = 20

    def get_queryset(self, **kwargs):
        return models.Meal.objects.filter(child=self.kwargs.get('child_id')).order_by("-dt")

class MealCreateView(LoginRequiredMixin,
                     mixins.AddChildContextViewMixin,
                     mixins.SetChildIdFormMixin,
                     mixins.CreatedByFormMixin,
                     CreateView):
    model = models.Meal
    template_name ="generic_form.html"
    pk_url_kwarg = "child_id"
    success_message = "Meal added."
    form_class = forms.MealForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Add meal"
        ctx["form"] = forms.MealForm(child = models.Child.objects.get(id=self.kwargs.get('child_id')))
        return ctx

    def get_success_url(self):
        return reverse_lazy('meals', kwargs = {'child_id': self.kwargs['child_id']})

class MealUpdateView(LoginRequiredMixin,
                     mixins.CheckObjectChildRelationMixin,
                     UpdateView):
    model = models.Meal
    template_name ="generic_form.html"
    success_message = "Meal details updated."
    form_class = forms.MealForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Edit meal details"
        return ctx

    def get_success_url(self):
        return reverse_lazy('meals', kwargs = {'child_id': self.kwargs['child_id']})

class MealDeleteView(LoginRequiredMixin,
                     mixins.CheckObjectChildRelationMixin,
                     DeleteView):
    model = models.Meal
    template_name ="generic_delete.html"
    success_message = "Meal deleted."

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Delete meal"
        ctx["delete_object_msg"] = (models.Meal.objects.get(id=self.kwargs['pk']))
        return ctx

    def get_success_url(self):
        return reverse_lazy('meals', kwargs = {'child_id': self.kwargs['child_id']})


class DiaperContentListView(LoginRequiredMixin,
                            mixins.AddChildContextViewMixin,
                            ListView):
    model = models.DiaperContent
    template_name ="generic_list.html"
    pk_url_kwarg = "child_id"
    paginate_by = 20

    def get_queryset(self, **kwargs):
        return models.DiaperContent.objects.filter(created_by=self.request.user.id).order_by("-dt")

class DiaperContentCreateView(LoginRequiredMixin,
                             mixins.AddChildContextViewMixin,
                             mixins.CreatedByFormMixin,
                             CreateView):
    model = models.DiaperContent
    template_name ="generic_form.html"
    pk_url_kwarg = "child_id"
    success_message = "DiaperContent added."
    form_class = forms.DiaperContentForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Add diaper content"
        return ctx

    def get_success_url(self):
        return reverse_lazy('diapercontents')

class DiaperContentUpdateView(LoginRequiredMixin,
                              mixins.AddChildContextViewMixin,
                              UpdateView):
    model = models.DiaperContent
    template_name ="generic_form.html"
    success_message = "DiaperContent details updated."
    form_class = forms.DiaperContentForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Edit diaper content details"
        return ctx

    def get_success_url(self):
        return reverse_lazy('diapercontents')


class DiaperListView(LoginRequiredMixin,
                     mixins.AddChildContextViewMixin,
                     ListView):
    model = models.Diaper
    pk_url_kwarg = "child_id"
    paginate_by = 20

    def get_queryset(self, **kwargs):
        return models.Diaper.objects.filter(child=self.kwargs.get('child_id')).order_by("-dt")

class DiaperCreateView(LoginRequiredMixin,
                       mixins.AddChildContextViewMixin,
                       mixins.SetChildIdFormMixin,
                       mixins.CreatedByFormMixin,
                       CreateView):
    model = models.Diaper
    template_name ="generic_form.html"
    pk_url_kwarg = "child_id"
    success_message = "Diaperchange added."
    form_class = forms.DiaperForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Add a changed diaper"
        ctx["form"] = forms.DiaperForm(child = models.Child.objects.get(id=self.kwargs.get('child_id')))
        return ctx

    def get_success_url(self):
        return reverse_lazy('diapers', kwargs = {'child_id': self.kwargs['child_id']})

class DiaperUpdateView(LoginRequiredMixin,
                       mixins.CheckObjectChildRelationMixin,
                       UpdateView):
    model = models.Diaper
    template_name ="generic_form.html"
    success_message = "Diaper details updated."
    form_class = forms.DiaperForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Edit diaperchange details"
        return ctx

    def get_success_url(self):
        return reverse_lazy('diapers', kwargs = {'child_id': self.kwargs['child_id']})

class DiaperDeleteView(LoginRequiredMixin,
                       mixins.CheckObjectChildRelationMixin,
                       DeleteView):
    model = models.Diaper
    template_name ="generic_delete.html"
    success_message = "Diaperchange details deleted."

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Delete diaperchange"
        ctx["delete_object_msg"] = str(models.Diaper.objects.get(id=self.kwargs['pk']))
        return ctx

    def get_success_url(self):
        return reverse_lazy('diapers', kwargs = {'child_id': self.kwargs['child_id']})


class EventListView(LoginRequiredMixin,
                    mixins.AddChildContextViewMixin,
                    ListView):
    model = models.Event
    pk_url_kwarg = "child_id"
    paginate_by = 20

    def get_queryset(self, **kwargs):
        return models.Event.objects.filter(child=self.kwargs.get('child_id')).order_by("-dt")

class EventCreateView(LoginRequiredMixin,
                      mixins.AddChildContextViewMixin,
                      mixins.SetChildIdFormMixin,
                      mixins.CreatedByFormMixin,
                      CreateView):
    model = models.Event
    template_name ="generic_form.html"
    pk_url_kwarg = "child_id"
    success_message = "Event added."
    form_class = forms.EventForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Add event"
        return ctx

    def get_success_url(self):
        return reverse_lazy('events', kwargs = {'child_id': self.kwargs['child_id']})

class EventUpdateView(LoginRequiredMixin,
                      mixins.CheckObjectChildRelationMixin,
                      UpdateView):
    model = models.Event
    template_name ="generic_form.html"
    success_message = "Event details updated."
    form_class = forms.EventForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Edit event details"
        return ctx

    def get_success_url(self):
        return reverse_lazy('events', kwargs = {'child_id': self.kwargs['child_id']})

class EventDeleteView(LoginRequiredMixin,
                      mixins.CheckObjectChildRelationMixin,
                      DeleteView):
    model = models.Event
    template_name ="generic_delete.html"
    success_message = "Event deleted."

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Delete event"
        ctx["delete_object_msg"] = str(models.Event.objects.get(id=self.kwargs['pk']))
        return ctx

    def get_success_url(self):
        return reverse_lazy('events', kwargs = {'child_id': self.kwargs['child_id']})


class DiaryEntryListView(LoginRequiredMixin,
                         mixins.AddChildContextViewMixin,
                         ListView):
    model = models.DiaryEntry
    pk_url_kwarg = "child_id"
    paginate_by = 20

    def get_queryset(self, **kwargs):
        return models.DiaryEntry.objects.filter(child=self.kwargs.get('child_id')).order_by("-dt")

class DiaryEntryCreateView(LoginRequiredMixin,
                           mixins.AddChildContextViewMixin,
                           mixins.SetChildIdFormMixin,
                           mixins.CreatedByFormMixin,
                           CreateView):
    model = models.DiaryEntry
    template_name ="generic_form.html"
    pk_url_kwarg = "child_id"
    success_message = "DiaryEntry added."
    form_class = forms.DiaryEntryForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Add diary entry"
        return ctx

    def get_success_url(self):
        return reverse_lazy('diary', kwargs = {'child_id': self.kwargs['child_id']})

class DiaryEntryUpdateView(LoginRequiredMixin,
                           mixins.CheckObjectChildRelationMixin,
                           UpdateView):
    model = models.DiaryEntry
    template_name ="generic_form.html"
    success_message = "Diary entry details updated."
    form_class = forms.DiaryEntryForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Edit diary entry"
        return ctx

    def get_success_url(self):
        return reverse_lazy('diary', kwargs = {'child_id': self.kwargs['child_id']})

class DiaryEntryDeleteView(LoginRequiredMixin,
                           mixins.CheckObjectChildRelationMixin,
                           DeleteView):
    model = models.DiaryEntry
    template_name ="generic_delete.html"
    success_message = "Diary entry deleted."

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Delete diary entry"
        ctx["delete_object_msg"] = str(models.DiaryEntry.objects.get(id=self.kwargs['pk']))
        return ctx

    def get_success_url(self):
        return reverse_lazy('diary', kwargs = {'child_id': self.kwargs['child_id']})


class SettingsUpdateView(LoginRequiredMixin,
                         UpdateView):
    model = models.UserSettings
    template_name ="generic_form.html"
    success_message = "Settings updated."
    form_class = forms.UserSettingsForm

    def get_context_data(self, **kwargs):
        if self.kwargs['pk'] != self.request.user.usersettings.id:
            raise PermissionDenied("Editing is only allowed for own settings.")

        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Edit user settings"
        return ctx

    def get_success_url(self):
        return reverse_lazy('settings')