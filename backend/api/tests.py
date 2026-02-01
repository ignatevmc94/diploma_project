
# Create your tests here.

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class UserThrottlingTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="throttle_user",
            email="throttle@test.com",
            password="12345678",
        )
        self.client.force_authenticate(user=self.user)

    def test_user_rate_throttling(self):
        """
        Проверка ограничения количества запросов от одного пользователя.
        """

        url = "/api/products/"

        # Первые 5 запросов проходят
        for _ in range(5):
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 6-й запрос должен быть заблокирован
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
