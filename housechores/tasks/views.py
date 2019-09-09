from django.shortcuts import render
from django.views import generic
from .models import Task


# Create your views here.
class IndexView(generic.ListView):
    template_name = 'tasks/index.html'

    def get_queryset(self):
        return Task.objects.order_by('-pub_date')