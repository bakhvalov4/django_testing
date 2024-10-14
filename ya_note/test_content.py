from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify
from notes.models import Note

User = get_user_model()


class TestHomePage(TestCase):

    HOME_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testuser')
        all_notes = []

        for index in range(10):
            title = f'Заметка {index}'
            notes = Note(
                title=title,
                text='Просто текст',
                author=cls.user,
                slug=slugify(title)
            )

            all_notes.append(notes)
        Note.objects.bulk_create(all_notes)

    def test_notes_order(self):
        self.client.force_login(self.user)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        all_slug = [notes.slug for notes in object_list]
        sorted_slug = sorted(all_slug)
        self.assertEqual(all_slug, sorted_slug)

    def test_notes_belong_to_user(self):
        other_user = User.objects.create(username='otheruser')
        Note.objects.create(title='Заметка другого пользователя', text='Текст',
                            author=other_user, slug='other-slug')

        self.client.force_login(self.user)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']

        # Проверяем, что заметки другого пользователя отсутствуют
        self.assertFalse(any(note.title == 'Заметка другого пользователя' for
                             note in object_list))

    def test_create_note_form(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('notes:add'))
        self.assertIn('form', response.context)

    def test_edit_note_form(self):
        note = Note.objects.first()
        self.client.force_login(self.user)
        response = self.client.get(reverse('notes:edit', args=[note.slug]))
        self.assertIn('form', response.context)
