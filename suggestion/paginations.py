from rest_framework.pagination import PageNumberPagination

class SuggestionPagination(PageNumberPagination):
    page_size = 10
