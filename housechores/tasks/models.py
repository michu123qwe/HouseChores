from django.db import models
from django.utils import timezone


# Create your models here.
class Task(models.Model):
    caption = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date added')
    due_date = models.DateTimeField('due date')
    task_giver = models.CharField(max_length=50)
    task_done_by = models.CharField(max_length=50, blank=True)
    task_done_date = models.DateTimeField('done date', blank=True, null=True)

    def __str__(self):
        return '{} by {}'.format(self.caption, self.task_giver)

    def is_expired(self):
        return not self.task_done_by and self.due_date < timezone.now()
