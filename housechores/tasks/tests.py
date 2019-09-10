from django.test import TestCase
from django.urls import reverse
from .models import Task
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from django.shortcuts import get_object_or_404


def create_task(text, status):
    """
    Create completed(status='completed'), uncompleted(status='uncompleted')
    or expired(status='expired') task
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


# Create your tests here.
class IndexViewTests(TestCase):
    def test_user_login(self):
        """
        User can log in and username is shown.
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        login = self.client.login(username='testuser', password='12345')

        response = self.client.get(reverse('tasks:index'))

        self.assertIs(login, True)
        self.assertContains(response, self.user.username)

    def test_user_logout(self):
        """
        User can log out.
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        logout = self.client.logout()

        response = self.client.get(reverse('tasks:index'))

        self.assertContains(response, 'You need to be logged in.')

    def test_user_not_logged_in(self):
        """
        If user is not logged in, appropriate message is displayed.
        """
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You need to be logged in.')

    def test_user_logged_in_no_tasks(self):
        """
        If user is logged in and there are no tasks,
        appropriate message is displayed
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No tasks are available.')
        self.assertQuerysetEqual(response.context['task_list'], [])

    def test_uncompleted_task(self):
        """
        Uncompleted tasks are displayed
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        create_task('a', 'uncompleted')
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['task_list'],
                                 ['<Task: a by a>'])

    def test_completed_task(self):
        """
        Completed tasks are displayed
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        create_task('a', 'completed')
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['task_list'],
                                 ['<Task: a by a>'])

    def test_expired_task(self):
        """
        Expired tasks are displayed
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        create_task('a', 'expired')
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['task_list'],
                                 ['<Task: a by a>'])

    def test_completed_and_uncompleted_task(self):
        """
        Both completed and uncompleted tasks are displayed
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        create_task('a', 'completed')
        create_task('b', 'uncompleted')
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['task_list'],
                                 ['<Task: b by b>', '<Task: a by a>'])

    def test_completed_and_expired_task(self):
        """
        Both completed and expired tasks are displayed
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        create_task('a', 'completed')
        create_task('b', 'expired')
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['task_list'],
                                 ['<Task: b by b>', '<Task: a by a>'])

    def test_uncompleted_and_expired_task(self):
        """
        Both uncompleted and expired tasks are displayed
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        create_task('a', 'uncompleted')
        create_task('b', 'expired')
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['task_list'],
                                 ['<Task: b by b>', '<Task: a by a>'])

    def test_completed_and_uncompleted_and_expired_task(self):
        """
        Completed, uncompleted and expired tasks are displayed
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        create_task('a', 'completed')
        create_task('b', 'uncompleted')
        create_task('c', 'expired')
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['task_list'],
                                 ['<Task: c by c>', '<Task: b by b>', '<Task: a by a>'])

    def test_completed_task_cannot_be_completed(self):
        """
        Completed task does not contain button to complete task.
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        create_task('a', 'completed')
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<button')

    def test_expired_task_cannot_be_completed(self):
        """
        Expired task does not contain button to complete task.
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        create_task('a', 'expired')
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<button')

    def test_uncompleted_task_can_be_completed(self):
        """
        Uncompleted task contains button to complete task.
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        create_task('a', 'uncompleted')
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<button')


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
        self.user = User.objects.create_user(username='testuser', password='12345')
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
        self.user = User.objects.create_user(username='testuser', password='12345')
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
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        task = create_task('a', 'expired')
        self.client.post(reverse('tasks:complete_task', args=(task.id,)))

        task_check = get_object_or_404(Task, pk=task.id)
        self.assertEqual(task_check.task_done_by, '')
        self.assertIsNone(task_check.task_done_date)


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