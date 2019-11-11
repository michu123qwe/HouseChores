from django.test import TestCase
from django.urls import reverse
from .models import Task
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from django.shortcuts import get_object_or_404

COMPLETE_BUTTON = 'class="btn btn-primary my-2"'
DELETE_BUTTON = 'class="btn btn-danger my-2"'


def create_user(superuser=False):
    if superuser:
        return User.objects.create_superuser(
            username='testuser', password='12345', email='aaa@gmail.com'
        )
    else:
        return User.objects.create_user(username='testuser', password='12345')


def create_task(text, status):
    """
    Create completed(status='completed'), uncompleted(status='uncompleted')
    or expired(status='expired') task
    Order in queryset(by due_date):
    completed(now-10days), expired(now-5days), uncompleted(now+10days)
    """
    pub_date = timezone.now() - datetime.timedelta(days=10)
    if status == 'completed':
        due_date = pub_date
        return Task.objects.create(caption=text, pub_date=pub_date,
                                   due_date=due_date, task_giver=text,
                                   task_done_by=text, task_done_date=timezone.now())
    elif status == 'uncompleted':
        due_date = timezone.now() + datetime.timedelta(days=10)
        return Task.objects.create(caption=text, pub_date=pub_date,
                                   due_date=due_date, task_giver=text)
    elif status == 'expired':
        due_date = timezone.now() - datetime.timedelta(days=5)
        return Task.objects.create(caption=text, pub_date=pub_date,
                                   due_date=due_date, task_giver=text)


# IndexView tests
class IndexViewTests(TestCase):

    def test_display_no_tasks(self):
        """
        If there are no tasks, appropriate message is displayed
        """
        self.user = create_user()
        self.client.login(username='testuser', password='12345')

        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<td>')
        self.assertQuerysetEqual(response.context['task_list'], [])

    def test_display_uncompleted_task(self):
        """
        Uncompleted tasks are displayed
        """
        self.user = create_user()
        self.client.login(username='testuser', password='12345')

        create_task('a', 'uncompleted')
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['task_list'],
                                 ['<Task: a by a>'])

    def test_display_completed_task(self):
        """
        Completed tasks are displayed
        """
        self.user = create_user()
        self.client.login(username='testuser', password='12345')

        create_task('a', 'completed')
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['task_list'],
                                 ['<Task: a by a>'])

    def test_display_expired_task(self):
        """
        Expired tasks are displayed
        """
        self.user = create_user()
        self.client.login(username='testuser', password='12345')

        create_task('a', 'expired')
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['task_list'],
                                 ['<Task: a by a>'])

    def test_display_completed_and_uncompleted_tasks(self):
        """
        Both completed and uncompleted (sorted by due_date) tasks are displayed
        """
        self.user = create_user()
        self.client.login(username='testuser', password='12345')

        create_task('a', 'completed')
        create_task('b', 'uncompleted')
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['task_list'],
                                 ['<Task: a by a>', '<Task: b by b>'])

    def test_display_completed_and_expired_tasks(self):
        """
        Both completed and expired (sorted by due_date) tasks are displayed
        """
        self.user = create_user()
        self.client.login(username='testuser', password='12345')

        create_task('a', 'completed')
        create_task('b', 'expired')
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['task_list'],
                                 ['<Task: a by a>', '<Task: b by b>'])

    def test_display_uncompleted_and_expired_tasks(self):
        """
        Both uncompleted and expired (sorted by due_date) tasks are displayed
        """
        self.user = create_user()
        self.client.login(username='testuser', password='12345')

        create_task('a', 'uncompleted')
        create_task('b', 'expired')
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['task_list'],
                                 ['<Task: b by b>', '<Task: a by a>'])

    def test_display_completed_and_uncompleted_and_expired_tasks(self):
        """
        Completed, uncompleted and expired (sorted by due_date) tasks are displayed
        """
        self.user = create_user()
        self.client.login(username='testuser', password='12345')

        create_task('a', 'completed')
        create_task('b', 'uncompleted')
        create_task('c', 'expired')
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['task_list'],
                                 ['<Task: a by a>', '<Task: c by c>', '<Task: b by b>'])

    def test_completed_task_cannot_be_completed(self):
        """
        Completed task does not contain 'Done' button to complete task.
        """
        self.user = create_user()
        self.client.login(username='testuser', password='12345')

        create_task('a', 'completed')
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Done</button>')

    def test_expired_task_cannot_be_completed(self):
        """
        Expired task does not contain 'Done' button to complete task.
        """
        self.user = create_user()
        self.client.login(username='testuser', password='12345')

        create_task('a', 'expired')
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, COMPLETE_BUTTON)

    def test_uncompleted_task_can_be_completed(self):
        """
        Uncompleted task contains 'Done' button to complete task.
        """
        self.user = create_user()
        self.client.login(username='testuser', password='12345')

        create_task('a', 'uncompleted')
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, COMPLETE_BUTTON)

    def test_can_create_task(self):
        """
        Logged user can create tasks.
        """
        self.user = create_user()
        self.client.login(username='testuser', password='12345')

        response = self.client.get(reverse('tasks:index'))
        self.assertContains(response, 'Create Task')

    def test_superuser_delete_others_task(self):
        """
        Superuser can delete other users' tasks
        """
        self.user = create_user(superuser=True)
        self.client.login(username='testuser', password='12345')

        create_task('a', 'completed')

        response = self.client.get(reverse('tasks:index'))
        self.assertContains(response, DELETE_BUTTON)

    def test_user_delete_owned_task(self):
        """
        User can delete task created by self
        """
        self.user = create_user()
        self.client.login(username='testuser', password='12345')

        create_task('testuser', 'completed')

        response = self.client.get(reverse('tasks:index'))
        self.assertContains(response, DELETE_BUTTON)

    def test_user_cannot_delete_not_owned_task(self):
        """
        User cannot delete task not created by self
        """
        self.user = create_user()
        self.client.login(username='testuser', password='12345')

        create_task('a', 'completed')

        response = self.client.get(reverse('tasks:index'))
        self.assertNotContains(response, DELETE_BUTTON)


# complete_task tests
class CompleteTaskViewTests(TestCase):
    def test_not_logged_user_complete_task(self):
        """
        Not logged user cannot complete tasks.
        """
        task = create_task('a', 'uncompleted')
        self.client.post(reverse('tasks:complete_task', args=(task.id,)))

        task_check = get_object_or_404(Task, pk=task.id)
        self.assertEqual(task_check.task_done_by, '')
        self.assertIsNone(task_check.task_done_date)

    def test_complete_uncompleted_task(self):
        """
        Logged user can complete uncompleted tasks.
        """
        self.user = create_user()
        self.client.login(username='testuser', password='12345')

        task = create_task('a', 'uncompleted')
        self.client.post(reverse('tasks:complete_task', args=(task.id,)))

        task_check = get_object_or_404(Task, pk=task.id)
        self.assertEqual(task_check.task_done_by, self.user.username)
        self.assertIsNotNone(task_check.task_done_date)

    def test_complete_completed_task(self):
        """
        Logged user cannot complete completed tasks.
        """
        self.user = create_user()
        self.client.login(username='testuser', password='12345')

        task = create_task('a', 'completed')
        self.client.post(reverse('tasks:complete_task', args=(task.id,)))

        task_check = get_object_or_404(Task, pk=task.id)
        self.assertEqual(task_check.task_done_by, 'a')
        self.assertEqual(task_check.task_done_date, task.task_done_date)

    def test_complete_expired_task(self):
        """
        Logged user cannot complete expired tasks.
        """
        self.user = create_user()
        self.client.login(username='testuser', password='12345')

        task = create_task('a', 'expired')
        self.client.post(reverse('tasks:complete_task', args=(task.id,)))

        task_check = get_object_or_404(Task, pk=task.id)
        self.assertEqual(task_check.task_done_by, '')
        self.assertIsNone(task_check.task_done_date)


# delete_task tests
class DeleteTaskViewTests(TestCase):
    def test_not_logged_user_delete_task(self):
        """
        Not logged user cannot delete tasks.
        """
        task = create_task('a', 'uncompleted')
        self.client.post(reverse('tasks:delete_task', args=(task.id,)))

        self.assertEqual(Task.objects.count(), 1)

    def test_user_delete_not_owned_task(self):
        """
        User cannot delete not owned task
        """
        self.user = create_user()
        self.client.login(username='testuser', password='12345')

        task = create_task('a', 'uncompleted')
        self.client.post(reverse('tasks:delete_task', args=(task.id,)))

        self.assertEqual(Task.objects.count(), 1)

    def test_user_delete_owned_task(self):
        """
        User can delete owned task
        """
        self.user = create_user()
        self.client.login(username='testuser', password='12345')

        task = create_task('testuser', 'uncompleted')
        self.client.post(reverse('tasks:delete_task', args=(task.id,)))

        self.assertEqual(Task.objects.count(), 0)

    def test_superuser_delete_not_owned_task(self):
        """
        Superuser can delete not owned task
        """
        self.user = create_user(superuser=True)
        self.client.login(username='testuser', password='12345')

        task = create_task('a', 'uncompleted')
        self.client.post(reverse('tasks:delete_task', args=(task.id,)))

        self.assertEqual(Task.objects.count(), 0)


# create_task tests
class CreateTaskViewTests(TestCase):
    def test_not_logged_user_create_task(self):
        """
        Not logged user cannot create tasks.
        """
        caption = 'a'
        date = timezone.now()
        self.client.post(reverse('tasks:create_task'), {'caption': caption, 'due_date': date})

        self.assertEqual(Task.objects.count(), 0)

    def test_logged_user_create_task(self):
        """
        Logged user can create tasks.
        """
        self.user = create_user()
        self.client.login(username='testuser', password='12345')

        caption = 'a'
        # date = timezone.now()
        date = timezone.localtime(timezone.now()).strftime('%d/%m/%Y %H:%M')

        self.client.post(reverse('tasks:create_task'), {'caption': caption, 'due_date': date})
        self.assertEqual(Task.objects.count(), 1)


# Task model tests
class TaskModelTests(TestCase):
    def test_completed_task(self):
        """
        Completed task is not expired.
        """
        due_date = timezone.now() - datetime.timedelta(days=10)
        task = Task.objects.create(caption='a', pub_date=timezone.now(),
                                   due_date=due_date, task_giver='a',
                                   task_done_by='a', task_done_date=timezone.now())
        self.assertIs(task.is_expired(), False)

        due_date = timezone.now() + datetime.timedelta(days=10)
        task = Task.objects.create(caption='a', pub_date=timezone.now(),
                                   due_date=due_date, task_giver='a',
                                   task_done_by='a', task_done_date=timezone.now())
        self.assertIs(task.is_expired(), False)

        due_date = timezone.now()
        task = Task.objects.create(caption='a', pub_date=timezone.now(),
                                   due_date=due_date, task_giver='a',
                                   task_done_by='a', task_done_date=timezone.now())
        self.assertIs(task.is_expired(), False)

    def test_due_date_after_now(self):
        """
        Task with 'due_date' after 'timezone.now()' is not expired
        """
        due_date = timezone.now() + datetime.timedelta(days=10)
        task = Task.objects.create(caption='a', pub_date=timezone.now(),
                                   due_date=due_date, task_giver='a')
        self.assertIs(task.is_expired(), False)

    def test_due_date_before_now(self):
        """
        Task with 'due_date' before 'timezone.now()' is expired
        """
        due_date = timezone.now() - datetime.timedelta(days=10)
        task = Task.objects.create(caption='a', pub_date=timezone.now(),
                                   due_date=due_date, task_giver='a')
        self.assertIs(task.is_expired(), True)

    def test_due_date_is_now(self):
        """
        Task with 'due_date' equal to 'timezone.now()' is expired
        """
        task = Task.objects.create(caption='a', pub_date=timezone.now(),
                                   due_date=timezone.now(), task_giver='a')
        self.assertIs(task.is_expired(), True)
