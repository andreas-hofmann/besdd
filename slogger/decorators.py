from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from . import models

def only_own_children(view):
    def wrapper(request, *args, **kwargs):
        child_id = kwargs.get('child_id')

        if not child_id:
            raise PermissionDenied("Invalid child requested")

        child = get_object_or_404(models.Child, id=child_id)

        if not request.user.is_authenticated:
            raise PermissionDenied("Invalid child requested")

        if (request.user not in child.parents.all()) and (request.user != child.created_by):
            raise PermissionDenied("Invalid child requested")

        return view(request, *args, **kwargs)
    
    return wrapper