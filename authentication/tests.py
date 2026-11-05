from django.test import TestCase
from django.contrib.auth.models import User

from .models import AccountProfile, BanUser


class GetProfileBanStatusTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='profile-user', password='test-password')
        AccountProfile.objects.create(user=self.user, email='profile-user@example.com')

    def test_profile_includes_false_ban_status_when_user_is_not_banned(self):
        response = self.client.get(f'/profile/{self.user.pk}')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['profile'][0]['ban'])

    def test_profile_includes_true_ban_status_when_user_is_banned(self):
        BanUser.objects.create(user=self.user, ban=True)

        response = self.client.get(f'/profile/{self.user.pk}')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['profile'][0]['ban'])
