import pytest
from news.models import Comment
from pytest_django.asserts import assertRedirects, assertFormError
from pytest_lazy_fixtures import lf
from news.forms import WARNING
from http import HTTPStatus


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, detail_url, form_data):
    client.post(detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_authorized_user_can_create_comment(
    author_client,
    author,
    news,
    detail_url,
    news_comments_url,
    form_data
):
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, news_comments_url)
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data.get('text')
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(
    author_client,
    detail_url,
    bad_words_form_data
):
    response = author_client.post(detail_url, data=bad_words_form_data)
    form = response.context['form']
    assertFormError(
        form=form,
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, http_status, expected_comments_count',
    (
        (lf('author_client'), HTTPStatus.FOUND, 0),
        (lf('not_author_client'), HTTPStatus.NOT_FOUND, 1),
    )
)
def test_delete_comment_availability(
    comment_delete_url,
    news_comments_url,
    parametrized_client,
    http_status,
    expected_comments_count
):
    response = parametrized_client.delete(comment_delete_url)
    assert response.status_code == http_status
    if http_status == HTTPStatus.FOUND:
        assertRedirects(response, news_comments_url)
    comments_count = Comment.objects.count()
    assert comments_count == expected_comments_count


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, specific_arg, expected_data',
    (
        (lf('author_client'), lf('news_comments_url'), lf('update_form_data')),
        (lf('not_author_client'), HTTPStatus.NOT_FOUND, lf('form_data')),
    )
)
def test_edit_comment_availability(
    comment,
    comment_edit_url,
    news_comments_url,
    update_form_data,
    parametrized_client,
    specific_arg,
    expected_data
):
    response = parametrized_client.post(
        comment_edit_url,
        data=update_form_data
    )
    if specific_arg == HTTPStatus.NOT_FOUND:
        assert response.status_code == specific_arg
    else:
        assertRedirects(response, news_comments_url)
    comment.refresh_from_db()
    assert comment.text == expected_data.get('text')
