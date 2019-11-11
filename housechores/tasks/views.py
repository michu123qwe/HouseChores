from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Task
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from .forms import CreateTaskForm
import pytz


# Create your views here.
class IndexView(generic.ListView):
    template_name = 'tasks/index.html'

    def get_queryset(self):
        return Task.objects.order_by('due_date')


def complete_task(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return HttpResponseRedirect(reverse('tasks:index'))

    # redirect to index when task can't be completed
    if task.task_done_by or not request.user.is_authenticated or task.is_expired():
        return HttpResponseRedirect(reverse('tasks:index'))

    # mark task as completed and redirect to index
    task.task_done_by = request.user.username
    task.task_done_date = timezone.now()
    task.save()

    return HttpResponseRedirect(reverse('tasks:index'))


def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    # redirect to index when user is not logged in or user does not own this task
    if not request.user.is_authenticated or \
            (not request.user.is_superuser and task.task_giver != request.user.username):
        return HttpResponseRedirect(reverse('tasks:index'))

    # delete task
    task.delete()

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

            # create new task
            task = Task()
            task.caption = request.POST['caption']
            task.pub_date = timezone.now()
            task.due_date = timezone.datetime(year=int(year), month=int(month),
                                              day=int(day), hour=int(hour),
                                              minute=int(minute),
                                              tzinfo=pytz.timezone('Europe/Warsaw'))
            task.task_giver = request.user.username

            task.save()
            return HttpResponseRedirect(reverse('tasks:index'))

    form = CreateTaskForm()
    return render(request, 'tasks/create_task.html', {'form': form})
