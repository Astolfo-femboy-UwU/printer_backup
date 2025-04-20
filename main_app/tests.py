from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile
from .forms import RegistrationForm, LoginForm, ProfileEditForm


class ViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        self.profile = Profile.objects.create(user=self.test_user)

    def test_welcome_page_view(self):
        response = self.client.get(reverse('welcome_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'welcome_page.html')

    def test_registration_page_view_get(self):
        response = self.client.get(reverse('registration_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/registration_page.html')
        self.assertIsInstance(response.context['reg_form'], RegistrationForm)

    def test_registration_page_view_post_success(self):
        data = {
            'username': 'new_user',
            'password': 'aComplex_pass123',
            'password2': 'aComplex_pass123',
            'email': 'new@example.com',
            'first_name': 'NewFirstName',
            'last_name': 'NewLastName'
        }
        response = self.client.post(reverse('registration_page'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='new_user').exists())

    def test_login_page_view_get(self):
        response = self.client.get(reverse('login_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertIsInstance(response.context['form'], LoginForm)

    def test_login_page_view_post_success(self):
        response = self.client.post(reverse('login_page'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_login_page_view_post_failure(self):
        response = self.client.post(reverse('login_page'), {
            'username': 'wrong_user',
            'password': 'wrong_pass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Неверное имя пользователя или пароль")

    def test_logout_page_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout_page'))
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, '/')

    def test_profile_page_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile.html')
        self.assertEqual(response.context['profile'], self.profile)

    def test_profile_page_view_unauthenticated(self):
        response = self.client.get(reverse('profile_page'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_edit_profile_page_view_get(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('edit_profile_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')
        self.assertIsInstance(response.context['form'], ProfileEditForm)

    def test_edit_profile_page_view_post_success(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            # Add other profile fields if your form has them
        }
        response = self.client.post(reverse('edit_profile_page'), data)
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, '/profile/')
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.first_name, 'Updated')

 #   def test_printers_page_view(self):
 #       response = self.client.get(reverse('printers_page'))
  #      self.assertEqual(response.status_code, 200)
  #      self.assertTemplateUsed(response, 'printers_page.html')

    # def test_custom_printers_page_view(self):
    #     response = self.client.get(reverse('custom_printers_page'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'custom_printer_page.html')

    def test_support_page_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('support_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'support_page.html')

    def test_support_page_view_unauthenticated(self):
        response = self.client.get(reverse('support_page'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login