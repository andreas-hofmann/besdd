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
from django.http import HttpResponse, JsonResponse
from django.utils import timezone as tz

from . import models
from . import forms
from . import functions
from . import mixins
from . import helpers
from . import decorators

# Free for all views

class IndexView(mixins.AddChildContextViewMixin,
                mixins.AjaxableResponseMixin,
                TemplateView):
    template_name = "slogger/index.html"

    def render_to_response(self, context, **response_kwargs):
        if self.request.user.is_authenticated:
            children = models.Child.objects.filter(parents__id=self.request.user.id)
            if self.request.user.is_authenticated:
                s = self.request.user.usersettings
                if s.default_child:
                    return redirect('child', child_id=s.default_child.id)

            if children:
                return redirect('child', child_id=children.reverse()[0].id)
            else:
                return redirect('child_add')
        return super().render_to_response(context, **response_kwargs)

    def get_json(self, request, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)

        if ctx.get('children'):
            my_children = ctx.get('children').all()
        else:
            my_children = []

        default_child = None
        if request.user.is_authenticated and request.user.usersettings.default_child:
            c = request.user.usersettings.default_child
            default_child = { "id": c.id, "name": c.name }

        return JsonResponse(
        {
            'user': request.user.username if request.user.is_authenticated else None,
            'id': request.user.id if request.user.is_authenticated else None,
            'default_child': default_child,
            'children': [
                {
                    'id': c.id,
                    'name': c.name,
                } for c in my_children
            ],
        })

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
                      mixins.AjaxableResponseMixin,
                      TemplateView):
    template_name = "slogger/plots/summary.html"

# Model views

class SleepPhaseListView(LoginRequiredMixin,
                         mixins.AddChildContextViewMixin,
                         mixins.AjaxableResponseMixin,
                         ListView):
    model = models.SleepPhase

    def setup(self, request, *args, **kwargs):
        self.paginate_by = request.user.usersettings.paginate_by
        return super().setup(request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        return models.SleepPhase.objects.filter(child=self.kwargs.get('child_id')).order_by("-dt")

    def get_json(self, request, *args, **kwargs):
        self.paginate_by = None
        data = models.SleepPhase.objects.filter(child=self.kwargs.get('child_id')).order_by("-dt")
        data = helpers.filter_GET_daterage(request, data)

        return JsonResponse(
            [{
                'id': d.id,
                'from': d.dt,
                'to': d.dt_end if d.dt_end else None,
            } for d in data.all() ],
        safe=False)

class SleepPhaseCreateView(LoginRequiredMixin,
                           SuccessMessageMixin,
                           mixins.AddChildContextViewMixin,
                           mixins.SetChildIdFormMixin,
                           mixins.CreatedByFormMixin,
                           mixins.AjaxableResponseMixin,
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
                           mixins.AjaxableResponseMixin,
                           UpdateView):
    model = models.SleepPhase
    template_name = "generic_form.html"
    success_message = "Sleepphase updated."
    form_class = forms.SleepPhaseForm

    def get_initial(self):
        initial = super().get_initial()
        try:
            if not self.object.dt_end:
                initial['dt_end'] = tz.now()
        except:
            pass
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["headline"] = "Update Sleepphase"
        return ctx
    
    def get_success_url(self):
        return reverse_lazy('sleepphases', kwargs = {'child_id': self.object.child.id})

    def get_json(self, request, *args, **kwargs):
        o = self.get_object()
        return JsonResponse({
            'id': o.id,
            'dt': o.dt,
            'dt_end': o.dt_end,
        })

class SleepPhaseDeleteView(LoginRequiredMixin,
                           SuccessMessageMixin,
                           mixins.AddChildContextViewMixin,
                           mixins.AjaxableResponseMixin,
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
                mixins.AjaxableResponseMixin,
                DetailView):
    model = models.Child
    pk_url_kwarg = "child_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["parents"] = [ p for p in get_user_model().objects.all() if p in self.object.parents.all() ]
        return context

    def get_json(self, request, *args, **kwargs):
        c = self.get_object()
        return JsonResponse(
        {
            'child': {
                'id': c.id,
                'name': c.name,
                'birthday': c.birthday,
                'parents': [
                    { 'id': p.id, 'name': p.username, } for p in c.parents.all()
                ],
            },
        })

class ChildCreateView(LoginRequiredMixin,
                      mixins.AddChildContextViewMixin,
                      mixins.CreatedByFormMixin,
                      mixins.AjaxableResponseMixin,
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

    def form_valid(self, form):
        ret = super().form_valid(form)
        new_child = form.save()
        new_child.parents.set({self.request.user})
        return ret

class ChildUpdateView(LoginRequiredMixin,
                      mixins.AddChildContextViewMixin,
                      mixins.AjaxableResponseMixin,
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

    def get_json(self, request, *args, **kwargs):
        o = self.get_object()
        return JsonResponse({
            'id': o.id,
            'name': o.name,
            'parents': o.parents.all(),
            'birthday': o.birthday,
            'gender': o.gender,
        })

class ChildListView(LoginRequiredMixin,
                    mixins.AddChildContextViewMixin,
                    mixins.AjaxableResponseMixin,
                    ListView):
    def get_queryset(self):
        return models.Child.objects.filter(parents__id=self.request.user.id)


class SummaryListView(LoginRequiredMixin,
                      mixins.AddChildContextViewMixin,
                      mixins.AjaxableResponseMixin,
                      ListView):
    template_name = "slogger/summary.html"

    def setup(self, request, *args, **kwargs):
        self.paginate_by = request.user.usersettings.paginate_by
        return super().setup(request, *args, **kwargs)

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
                          mixins.AjaxableResponseMixin,
                          ListView):
    model = models.Measurement
    pk_url_kwarg = "child_id"

    def setup(self, request, *args, **kwargs):
        self.paginate_by = request.user.usersettings.paginate_by
        return super().setup(request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        return models.Measurement.objects.filter(child=self.kwargs.get('child_id')).order_by("-dt")

    def get_json(self, request, *args, **kwargs):
        self.paginate_by = None
        data = models.Measurement.objects.filter(child=self.kwargs.get('child_id')).order_by("-dt")
        data = helpers.filter_GET_daterage(request, data)

        return JsonResponse(
            [{
                'id': d.id,
                'time': tz.localtime(d.dt),
                'height': d.height,
                'weight': d.weight,
            } for d in data.all() ],
        safe=False)

class MeasurementCreateView(LoginRequiredMixin,
                            mixins.AddChildContextViewMixin,
                            mixins.SetChildIdFormMixin,
                            mixins.CreatedByFormMixin,
                            mixins.AjaxableResponseMixin,
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
                            mixins.AjaxableResponseMixin,
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

    def get_json(self, request, *args, **kwargs):
        o = self.get_object()
        return JsonResponse({
            'id': o.id,
            'dt': o.dt,
            'height': o.height,
            'weight': o.weight,
        })

class MeasurementDeleteView(LoginRequiredMixin,
                            mixins.CheckObjectChildRelationMixin,
                            mixins.AjaxableResponseMixin,
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
                   mixins.AjaxableResponseMixin,
                   ListView):
    model = models.Food
    pk_url_kwarg = "child_id"

    def setup(self, request, *args, **kwargs):
        self.paginate_by = request.user.usersettings.paginate_by
        return super().setup(request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        return models.Food.objects.filter(created_by=self.request.user.id).order_by("-dt")

    def get_json(self, request, *args, **kwargs):
        o = self.get_object()
        return JsonResponse({
            'id': o.id,
            'name': o.name,
            'description': o.description,
        })

class FoodCreateView(LoginRequiredMixin,
                     mixins.AddChildContextViewMixin,
                     mixins.CreatedByFormMixin,
                     mixins.AjaxableResponseMixin,
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
                     mixins.CheckCreatedByMixin,
                     mixins.AjaxableResponseMixin,
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

    def get_json(self, request, *args, **kwargs):
        o = self.get_object()
        return JsonResponse({
            'id': o.id,
            'dt': o.dt,
            'name': o.name,
            'description': o.description,
        })


class MealListView(LoginRequiredMixin,
                   mixins.AddChildContextViewMixin,
                   mixins.AjaxableResponseMixin,
                   ListView):
    model = models.Meal
    pk_url_kwarg = "child_id"

    def setup(self, request, *args, **kwargs):
        self.paginate_by = request.user.usersettings.paginate_by
        return super().setup(request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        return models.Meal.objects.filter(child=self.kwargs.get('child_id')).order_by("-dt")

    def get_json(self, request, *args, **kwargs):
        self.paginate_by = None
        data = models.Meal.objects.filter(child=self.kwargs.get('child_id')).order_by("-dt")
        data = helpers.filter_GET_daterage(request, data)

        return JsonResponse(
            [{
                'id': d.id,
                'time': tz.localtime(d.dt),
                'food': [ f.name for f in d.food.all() ],
            } for d in data.all() ],
        safe=False)

class MealCreateView(LoginRequiredMixin,
                     mixins.AddChildContextViewMixin,
                     mixins.SetChildIdFormMixin,
                     mixins.CreatedByFormMixin,
                     mixins.AjaxableResponseMixin,
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
                     mixins.AjaxableResponseMixin,
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

    def get_json(self, request, *args, **kwargs):
        child = models.Child.objects.get(id=self.kwargs['child_id'])
        foods = models.Food.objects.filter( Q(created_by__in=child.parents.all()) | Q(is_default=True))

        o = self.get_object()
        return JsonResponse({
            'id': o.id,
            'dt': o.dt,
            'food': o.food.all(),
            'food_choices': [ f for f in foods.all() ],
        })

class MealDeleteView(LoginRequiredMixin,
                     mixins.CheckObjectChildRelationMixin,
                     mixins.AjaxableResponseMixin,
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
                            mixins.AjaxableResponseMixin,
                            ListView):
    model = models.DiaperContent
    pk_url_kwarg = "child_id"

    def setup(self, request, *args, **kwargs):
        self.paginate_by = request.user.usersettings.paginate_by
        return super().setup(request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        return models.DiaperContent.objects.filter(created_by=self.request.user.id).order_by("-dt")

class DiaperContentCreateView(LoginRequiredMixin,
                             mixins.AddChildContextViewMixin,
                             mixins.CreatedByFormMixin,
                             mixins.AjaxableResponseMixin,
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
                              mixins.CheckCreatedByMixin,
                              mixins.AjaxableResponseMixin,
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

    def get_json(self, request, *args, **kwargs):
        o = self.get_object()
        return JsonResponse({
            'id': o.id,
            'name': o.name,
            'description': o.description,
        })


class DiaperListView(LoginRequiredMixin,
                     mixins.AddChildContextViewMixin,
                     mixins.AjaxableResponseMixin,
                     ListView):
    model = models.Diaper
    pk_url_kwarg = "child_id"

    def setup(self, request, *args, **kwargs):
        self.paginate_by = request.user.usersettings.paginate_by
        return super().setup(request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        return models.Diaper.objects.filter(child=self.kwargs.get('child_id')).order_by("-dt")

    def get_json(self, request, *args, **kwargs):
        self.paginate_by = None
        data = models.Diaper.objects.filter(child=self.kwargs.get('child_id')).order_by("-dt")
        data = helpers.filter_GET_daterage(request, data)

        return JsonResponse(
            [{
                'id': d.id,
                'time': tz.localtime(d.dt),
                'contents': [ c.name for c in d.content.all() ],
            } for d in data.all() ],
        safe=False)

class DiaperCreateView(LoginRequiredMixin,
                       mixins.AddChildContextViewMixin,
                       mixins.SetChildIdFormMixin,
                       mixins.CreatedByFormMixin,
                       mixins.AjaxableResponseMixin,
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
                       mixins.AjaxableResponseMixin,
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

    def get_json(self, request, *args, **kwargs):
        child = models.Child.objects.get(id=self.kwargs['child_id'])
        dc = models.DiaperContent.objects.filter( Q(created_by__in=child.parents.all()) | Q(is_default=True))

        o = self.get_object()
        return JsonResponse({
            'id': o.id,
            'dt': o.dt,
            'content': o.content.all(),
            'content_choices': [ f for f in dc.all() ],
        })

class DiaperDeleteView(LoginRequiredMixin,
                       mixins.CheckObjectChildRelationMixin,
                       mixins.AjaxableResponseMixin,
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
                    mixins.AjaxableResponseMixin,
                    ListView):
    model = models.Event
    pk_url_kwarg = "child_id"

    def setup(self, request, *args, **kwargs):
        self.paginate_by = request.user.usersettings.paginate_by
        return super().setup(request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        return models.Event.objects.filter(child=self.kwargs.get('child_id')).order_by("-dt")

    def get_json(self, request, *args, **kwargs):
        self.paginate_by = None
        data = models.Event.objects.filter(child=self.kwargs.get('child_id')).order_by("-dt")
        data = helpers.filter_GET_daterage(request, data)

        return JsonResponse(
            [{
                'id': d.id,
                'time': tz.localtime(d.dt),
                'event': d.event,
                'description': d.description,
            } for d in data.all() ],
        safe=False)

class EventCreateView(LoginRequiredMixin,
                      mixins.AddChildContextViewMixin,
                      mixins.SetChildIdFormMixin,
                      mixins.CreatedByFormMixin,
                      mixins.AjaxableResponseMixin,
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
                      mixins.AjaxableResponseMixin,
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

    def get_json(self, request, *args, **kwargs):
        o = self.get_object()
        return JsonResponse({
            'id': o.id,
            'dt': o.dt,
            'event': o.event,
            'description': o.description,
        })

class EventDeleteView(LoginRequiredMixin,
                      mixins.CheckObjectChildRelationMixin,
                      mixins.AjaxableResponseMixin,
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
                         mixins.AjaxableResponseMixin,
                         ListView):
    model = models.DiaryEntry
    pk_url_kwarg = "child_id"

    def setup(self, request, *args, **kwargs):
        self.paginate_by = request.user.usersettings.paginate_by
        return super().setup(request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        return models.DiaryEntry.objects.filter(child=self.kwargs.get('child_id')).order_by("-dt")

    def get_json(self, request, *args, **kwargs):
        self.paginate_by = None
        data = models.DiaryEntry.objects.filter(child=self.kwargs.get('child_id')).order_by("-dt")
        data = helpers.filter_GET_daterage(request, data)

        return JsonResponse(
            [{
                'id': d.id,
                'time': tz.localtime(d.dt),
                'title': d.event,
                'content': d.content,
            } for d in data.all() ],
        safe=False)

class DiaryEntryCreateView(LoginRequiredMixin,
                           mixins.AddChildContextViewMixin,
                           mixins.SetChildIdFormMixin,
                           mixins.CreatedByFormMixin,
                           mixins.AjaxableResponseMixin,
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
                           mixins.AjaxableResponseMixin,
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

    def get_json(self, request, *args, **kwargs):
        o = self.get_object()
        return JsonResponse({
            'id': o.id,
            'dt': o.dt,
            'title': o.title,
            'content': o.content,
        })

class DiaryEntryDeleteView(LoginRequiredMixin,
                           mixins.CheckObjectChildRelationMixin,
                           mixins.AjaxableResponseMixin,
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
                         mixins.AjaxableResponseMixin,
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

        form = ctx.get("form")
        if form:
            form.fields['default_child'].queryset = models.Child.objects.filter(
                parents=self.request.user
            )
        return ctx

    def get_success_url(self):
        return reverse_lazy('settings', kwargs= {'pk': self.request.user.usersettings.id })

    def get_json(self, request, *args, **kwargs):
        o = self.get_object()
        return JsonResponse({
            'id': o.id,
            'paginate_by': o.paginate_by,
            'date_range_days': o.date_range_days,
            'content': o.content,
            'sleep_enabled': o.sleep_enabled,
            'meals_enabled': o.meals_enabled,
            'diapers_enabled': o.diapers_enabled,
            'default_child': o.default_child,
            'start_hour_day': o.start_hour_day,
            'start_hour_night': o.start_hour_night,
            'histogram_raster': o.histogram_raster,
            'histogram_factor_md': o.histogram_factor_md,
        })