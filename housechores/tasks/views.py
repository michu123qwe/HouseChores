from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Task
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from .forms import CreateTaskForm
import datetime


# Create your views here.
class IndexView(generic.ListView):
    template_name = 'tasks/index.html'

    def get_queryset(self):
        return Task.objects.order_by('-due_date')


def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    # redirect to index when task can't be completed
    if task.task_done_by or not request.user.is_authenticated or task.is_expired():
        return HttpResponseRedirect(reverse('tasks:index'))

    # mark task as completed and redirect to index
    task.task_done_by = request.user.username
    task.task_done_date = timezone.now()
    task.save()

    return HttpResponseRedirect(reverse('tasks:index'))


def create_task(request):
    # redirect to index if user is not logged in
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('tasks:index'))

    if request.method == 'POST':
        form = CreateTaskForm(request.POST)
        if form.is_valid():

            # create convenient format for date
            date, time = request.POST['due_date'].split(' ')
            day, month, year = date.split('/')
            hour, minute = time.split(':')
            due_date = '{}-{}-{} {}:{}'.format(year, month, day, hour, minute)

            # create new task
            task = Task()
            task.caption = request.POST['caption']
            task.pub_date = timezone.now()
            task.due_date = due_date
            task.task_giver = request.user.username

            task.save()
            return HttpResponseRedirect(reverse('tasks:index'))

    form = CreateTaskForm()
    return render(request, 'tasks/create_task.html', {'form': form})

