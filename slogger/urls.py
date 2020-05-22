from django.urls import path, re_path

from . import views
from . import json

from django.views.generic import TemplateView

urlpatterns = [
    path('children/',                               views.ChildListView.as_view(),          name="children"),
    path('children/add/',                           views.ChildCreateView.as_view(),        name="child_add"),
    path('children/<int:child_id>/edit/',           views.ChildUpdateView.as_view(),        name="child_edit"),

    path('settings/<int:pk>/',                      views.SettingsUpdateView.as_view(),     name="settings"),

    path('foods/',                                  views.FoodListView.as_view(),           name="foods"),
    path('foods/add/',                              views.FoodCreateView.as_view(),         name="foods_add"),
    path('foods/edit/<int:pk>/',                    views.FoodUpdateView.as_view(),         name="foods_edit"),
    path('diapercontents/',                         views.DiaperContentListView.as_view(),  name="diapercontents"),
    path('diapercontents/add/',                     views.DiaperContentCreateView.as_view(),name="diapercontents_add"),
    path('diapercontents/edit/<int:pk>/',           views.DiaperContentUpdateView.as_view(),name="diapercontents_edit"),

    path('<int:child_id>/sleep/quickadd/',          views.quick_add_sleepphase,             name="sleepphases_quickadd"),

    path('<int:child_id>/sleep/',                   views.SleepPhaseListView.as_view(),     name="sleepphases"),
    path('<int:child_id>/sleep/add/',               views.SleepPhaseCreateView.as_view(),   name="sleepphases_add"),

    path('<int:child_id>/sleep/edit/<int:pk>/',     views.SleepPhaseUpdateView.as_view(),   name="sleepphases_edit"),
    path('<int:child_id>/sleep/delete/<int:pk>/',   views.SleepPhaseDeleteView.as_view(),   name="sleepphases_delete"),

    path('<int:child_id>/measurements/',            views.MeasurementListView.as_view(),    name="measurements"),
    path('<int:child_id>/measurements/add/',        views.MeasurementCreateView.as_view(),  name="measurements_add"),
    path('<int:child_id>/measurements/edit/<int:pk>/',   views.MeasurementUpdateView.as_view(), name="measurements_edit"),
    path('<int:child_id>/measurements/delete/<int:pk>/', views.MeasurementDeleteView.as_view(), name="measurements_delete"),
    path('<int:child_id>/meals/',                   views.MealListView.as_view(),           name="meals"),
    path('<int:child_id>/meals/add/',               views.MealCreateView.as_view(),         name="meals_add"),
    path('<int:child_id>/meals/edit/<int:pk>/',     views.MealUpdateView.as_view(),         name="meals_edit"),
    path('<int:child_id>/meals/delete/<int:pk>/',   views.MealDeleteView.as_view(),         name="meals_delete"),
    path('<int:child_id>/diapers/',                 views.DiaperListView.as_view(),         name="diapers"),
    path('<int:child_id>/diapers/add/',             views.DiaperCreateView.as_view(),       name="diapers_add"),
    path('<int:child_id>/diapers/edit/<int:pk>/',   views.DiaperUpdateView.as_view(),       name="diapers_edit"),
    path('<int:child_id>/diapers/delete/<int:pk>/', views.DiaperDeleteView.as_view(),       name="diapers_delete"),
    path('<int:child_id>/events/',                  views.EventListView.as_view(),          name="events"),
    path('<int:child_id>/events/add/',              views.EventCreateView.as_view(),        name="events_add"),
    path('<int:child_id>/events/edit/<int:pk>/',    views.EventUpdateView.as_view(),        name="events_edit"),
    path('<int:child_id>/events/delete/<int:pk>/',  views.EventDeleteView.as_view(),        name="events_delete"),
    path('<int:child_id>/diary/',                   views.DiaryEntryListView.as_view(),     name="diary"),
    path('<int:child_id>/diary/add/',               views.DiaryEntryCreateView.as_view(),   name="diary_add"),
    path('<int:child_id>/diary/edit/<int:pk>/',     views.DiaryEntryUpdateView.as_view(),   name="diary_edit"),
    path('<int:child_id>/diary/delete/<int:pk>/',   views.DiaryEntryDeleteView.as_view(),   name="diary_delete"),

    path('<int:child_id>/summary/',                 views.SummaryListView.as_view(),        name="summary"),
    path('<int:child_id>/plot/summary/',            views.SummaryPlotView.as_view(),        name="plot_summary"),


    path('<int:child_id>/data/check/',              json.get_check,                         name="check_data"),
    path('<int:child_id>/data/summary/graph/',      json.get_summary_data_graph,            name="summary_data_graph"),
    path('<int:child_id>/data/summary/list/',       json.get_summary_data_list,             name="summary_data_list"),
    path('<int:child_id>/data/histogram/',          json.get_histogram_data,                name="histogram_data"),
    path('<int:child_id>/data/measurements/',       json.get_growth_data,                   name="measurement_data"),
    path('<int:child_id>/data/percentiles/<str:m_type>/', json.get_percentile_data,         name="percentile_data"),


    path('<int:child_id>/',                         views.ChildView.as_view(),              name="child"),

    path('index/',                                  views.IndexView.as_view(),              name="index"),

    re_path('.*',                                        TemplateView.as_view(template_name="app.html"), name="app"),
]
