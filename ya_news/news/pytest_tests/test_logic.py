from http import HTTPStatus

import pytest

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

COMMENT_TEXT = 'Текст комментария'


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, url):
    form_data = {'text': COMMENT_TEXT}
    client.post(url, data=form_data)
    comments_count = Comment.objects.exists()
    assert not comments_count


def test_user_can_create_comment(author, author_client, url):
    form_data = {'text': COMMENT_TEXT}
    response = author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{url}#comments'
    comments_count = Comment.objects.count()
    assert comments_count
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news.title == 'Тестовая новость'
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    assert response.context['form'].errors['text'] == [WARNING]
    comments_count = Comment.objects.exists()
    assert not comments_count


def test_author_can_delete_comment(author_client, delete_url):
    response = author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    comments_count = Comment.objects.exists()
    assert not comments_count


def test_user_cant_delete_comment_of_another_user(not_author_client,
                                                  delete_url):
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.exists()
    assert comments_count


def test_author_can_edit_comment(author_client, edit_url, form_data, comment):
    response = author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(not_author_client, edit_url,
                                                form_data, comment):
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text == 'Комментарий'
