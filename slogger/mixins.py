from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse

from . import models


class AddChildContextViewMixin:
    """
    Mixin to add the currently selected child to the view context. Raises an
    error if the selected child does not have the current user as parent.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:

            child = None
            child_id = ''

            try:
                child_id = self.kwargs['child_id']
            except KeyError:
                pass

            if child_id:
                child = get_object_or_404(models.Child, id=child_id)

            children = models.Child.objects.filter(parents__id=self.request.user.id)

            if child and not (child in children or self.request.user == child.created_by ):
                raise PermissionDenied("Invalid child requested")

            context["child"] = child
            context["children"] = children

        return context


class CheckObjectChildRelationMixin(AddChildContextViewMixin):
    """
    Mixin to check whether the edited object was created by the current user.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            child = context['child']
        except KeyError:
            raise PermissionDenied("Invalid child requested")

        if self.object.child.id != child.id:
            raise PermissionDenied("Invalid child requested")

        return context

    def form_valid(self, form):
        # Call get_context_data() just to get the permission checks implemented there.
        self.get_context_data()
        return super().form_valid(form)


class CheckCreatedByMixin:
    """
    Mixin to check whether the edited object does belong to the currently
    selected child.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.object.created_by != self.request.user:
            raise PermissionDenied("Invalid object requested")

        return context

    def form_valid(self, form):
        if self.object.created_by != self.request.user:
            raise PermissionDenied("Invalid object requested")
        return super().form_valid(form)


class SetChildIdFormMixin:
    """
    Mixin to add the currently selected child to the child field of the
    created model.
    """

    def form_valid(self, form):
        form.instance.child = get_object_or_404(models.Child, id=self.kwargs.get('child_id'))
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        initial['child'] = models.Child.objects.get(id=self.kwargs.get('child_id'))
        return initial


class CreatedByFormMixin:
    """
    Mixin to add the current user to the created_by field of the created
    model.
    """

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        initial['created_by'] = self.request.user
        return initial


class AttributeModelMixin:
    """
    Mixin to remove certain fields from a model when presenting the form.
    """

    SKIP_FIELDS=(
        "id",
        "is_default",
        "created_by",
    )

    def get_attribute_names(self):
        return [ field.verbose_name for field in self._meta.fields
                if field.name not in self.SKIP_FIELDS ]

    def get_attribute_contents(self):
        return [ getattr(self, field.name) for field in self._meta.fields
                if field.name not in self.SKIP_FIELDS ]


class AjaxableResponseMixin:
    """
    Mixin to add AJAX support to a (form) view.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super().form_valid(form)
        if self.request.is_ajax():
            data = {
                'id': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response

    def get(self, request, *args, **kwargs):
        if not request.is_ajax():
            return super().get(request, *args, **kwargs)
        else:
            return self.get_json(request, *args, **kwargs)

    def get_json(self, request, *args, **kwargs):
        return JsonResponse({'Error': 'Not implemented!'}, status=501)
