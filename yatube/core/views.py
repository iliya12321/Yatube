from django.shortcuts import render
from http import HTTPStatus


def page_not_found(request, exception):
    return render(
        request, 'core/404.html', {'path': request.path}, HTTPStatus.NOT_FOUND
    )


def server_error(request):
    return render(request, 'core/500.html', HTTPStatus.INTERNAL_SERVER_ERROR)


def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html')
