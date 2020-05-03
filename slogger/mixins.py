from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from . import models


class AddChildContextViewMixin:

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            child = context['child']
        except KeyError:
            raise PermissionDenied("Invalid child requested")

        if self.object.child.id != child.id:
            raise PermissionDenied("Invalid child requested")

        return context


class SetChildIdFormMixin:

    def form_valid(self, form):
        form.instance.child = get_object_or_404(models.Child, id=self.kwargs.get('child_id'))
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        initial['child'] = models.Child.objects.get(id=self.kwargs.get('child_id'))
        return initial


class CreatedByFormMixin:

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        initial['created_by'] = self.request.user
        return initial


class AttributeModelMixin:

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