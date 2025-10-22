from http import HTTPStatus
import pytest
from pytest_lazy_fixtures import lf
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (lf('home_url'), lf('login_url'), lf('signup_url'))
)
def test_pages_availability_for_anonymous_user(client, url):
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_availability_for_anonymous_user(client, detail_url):
    response = client.get(detail_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url',
    (lf('comment_edit_url'), lf('comment_delete_url'))
)
def test_availability_for_comment_edit_and_delete(author_client, url):
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (lf('comment_edit_url'), lf('comment_delete_url'))
)
def test_redirects(client, login_url, url):
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'url',
    (lf('comment_edit_url'), lf('comment_delete_url'))
)
def test_pages_availability_for_not_author(not_author_client, url):
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
