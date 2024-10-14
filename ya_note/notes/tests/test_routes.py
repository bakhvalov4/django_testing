from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create(username='testuser')
        cls.note = Note.objects.create(title='Заголовок', text='Текст',
                                       author=cls.user)

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('notes:add', None),
            ('notes:detail', (self.note.id,)),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                if name not in ['notes:add', 'notes:detail']:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
