from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def secs_to_h(seconds):
    return f"{seconds/3600.0:04.01f}h"

@register.filter
def dt_localdate(dt):
    if dt:
        return timezone.localdate(dt)
    else:
        return ""

@register.filter
def dt_localtime(dt):
    if dt:
        return timezone.localtime(dt).time()
    else:
        return ""

@register.filter
def as_table_header(model, attributes=""):
    def tableize(field):
        a = ""
        if (attributes):
            a = " " + attributes + " "
        return "<th"+a+">" + str(field) + "</th>"

    output = "<tr>"

    for field in model.get_attribute_names():
        output += tableize(field)

    return output + "</tr>"

@register.filter
def as_table_row(model, attributes=""):
    def tableize(field):
        a = ""
        if (attributes):
            a = " " + attributes + " "
        return "<td" + a +">" + str(field) + "</td>"

    output = "<tr>"

    for field in model.get_attribute_contents():
        output += tableize(field)

    return output + "</tr>"