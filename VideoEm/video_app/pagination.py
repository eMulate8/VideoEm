from rest_framework.pagination import CursorPagination


class VideoCursorPagination(CursorPagination):
    page_size = 10
    ordering = '-time_created'
    cursor_query_param = 'cursor'


class HistoryCursorPagination(CursorPagination):
    page_size = 20
    ordering = '-watched_at'
    cursor_query_param = 'cursor'
