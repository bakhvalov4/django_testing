import pytest

from django.urls import reverse
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.test.client import Client
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def comment(author):
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Комментарий'
    )
    return comment


@pytest.fixture
def id_for_args(comment):
    return (comment.id,)


@pytest.fixture
def news_data():
    today = datetime.today()
    all_news = []

    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        all_news.append(news)
    News.objects.bulk_create(all_news)


@pytest.fixture
def news_with_comments(author):
    news = News.objects.create(
        title='Тестовая новость', text='Просто текст.'
    )
    now = timezone.now()
    for index in range(10):
        Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
            created=now + timedelta(days=index)
        )
    return news


@pytest.fixture
def detail_url(news_with_comments):
    return reverse('news:detail', args=(news_with_comments.id,))


@pytest.fixture
def url():
    news = News.objects.create(
        title='Тестовая новость',
        text='Текст заметки',
    )
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def form_data():
    return {'text': 'Обновлённый комментарий'}
