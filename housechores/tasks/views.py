from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Task
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse


# Create your views here.
class IndexView(generic.ListView):
    template_name = 'tasks/index.html'

    def get_queryset(self):
        return Task.objects.order_by('-pub_date')


def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if task.task_done_by or not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('tasks:index'))

    task.task_done_by = request.user.username
    task.task_done_date = timezone.now()
    task.save()

    return HttpResponseRedirect(reverse('tasks:index'))
