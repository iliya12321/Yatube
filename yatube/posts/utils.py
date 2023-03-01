from django.core.paginator import Paginator

QUERY_LIMIT = 10  # Количесво страниц выводимых на одной странице


def get_page_paginator(queryset, request):
    """Пагинация"""
    paginator = Paginator(queryset, QUERY_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
