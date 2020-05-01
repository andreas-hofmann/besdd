from django.views.generic import TemplateView, ListView, CreateView, FormView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from django.contrib.auth.forms import UserCreationForm

class RegistrationView(CreateView):
    template_name = "registration/register.html"
    model = get_user_model()
    form_class = UserCreationForm
    def get_success_url(self):
        return reverse_lazy("login")
