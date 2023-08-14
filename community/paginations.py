from rest_framework.pagination import PageNumberPagination

class CommunityPagination(PageNumberPagination):
    page_size = 10

class CommunityCommentPagination(PageNumberPagination):
    page_size = 10