from http import HTTPStatus

from django.shortcuts import render


def page_not_found(request, exception):
    """Ошибка 404"""
    return render(
        request, 'core/404.html',
        {'path': request.path},
        status=HTTPStatus.NOT_FOUND,
    )


def server_error(request):
    """Ошибка 500"""
    return render(
        request,
        'core/500.html',
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
    )


def csrf_failure(request, reason=''):
    """Ошибка 403"""
    return render(request, 'core/403csrf.html', status=HTTPStatus.FORBIDDEN)
