from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


# Create your tests here.
class UserAccountTests(TestCase):
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
        self.client.logout()

        response = self.client.get(reverse('tasks:index'))

        self.assertContains(response, 'You need to be logged in.')

    def test_user_not_logged_in(self):
        """
        If user is not logged in, appropriate message is displayed.
        """
        response = self.client.get(reverse('tasks:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You need to be logged in.')
