from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.forms import NoteForm, WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='testuser')
        cls.notes = Note.objects.create(title='Заголовок', text='Текст',
                                        author=cls.author)
        cls.url = reverse('notes:add')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {'title': 'Новый заголовок', 'text': 'Текст'}

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, '/done/')
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)
        notes = Note.objects.last()
        self.assertEqual(notes.text, self.form_data['text'])
        self.assertEqual(notes.title, self.form_data['title'])
        self.assertEqual(notes.author, self.author)

    def test_anonymous_user_cannot_create_note(self):
        response = self.client.post(self.url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_non_unique_title_raises_error(self):
        form_data = {'title': 'Заголовок', 'text': 'Текст',
                     'slug': self.notes.slug}
        form = NoteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(WARNING, form.errors['slug'][0])

    def test_slug_is_generated_if_not_provided(self):
        form_data = {'title': 'Новая заметка', 'text': 'Текст'}
        response = self.auth_client.post(self.url, data=form_data)
        self.assertRedirects(response, '/done/')
        note = Note.objects.last()
        self.assertIsNotNone(note.slug)


class TestNoteDelEdit(TestCase):
    TITLE = 'Заголовок'
    TEXT = 'Текст'
    NEW_TEXT = 'Новый текст'
    NEW_TITLE = 'Новый заголовок'

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='testuser')
        cls.notes = Note.objects.create(title=cls.TITLE, text=cls.TEXT,
                                        author=cls.author)
        cls.url = reverse('notes:success')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.edit_url = reverse('notes:edit', args=(cls.notes.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.notes.slug,))
        cls.form_data = {'text': cls.NEW_TEXT, 'title': cls.NEW_TITLE}

    def test_author_can_delete_note(self):
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, self.url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_reader_cant_delete_note(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.url)
        edited_note = Note.objects.get(id=self.notes.id)
        self.assertEqual(edited_note.text, self.NEW_TEXT)
        self.assertEqual(edited_note.title, self.NEW_TITLE)

    def test_reader_can_edit_note(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.text, self.TEXT)
        self.assertEqual(self.notes.title, self.TITLE)
