from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status, filters
from rest_framework.response import Response
from .models import Suggestion, SuggestionComment, SuggestionImage
from .serializers import SuggestionSerializer, SuggestionCreateSerailizer, SuggestionDetailSerializer, SuggestionCommentSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from .permissions import IsOwnerOrReadOnly
from .paginations import SuggestionPagination

# Create your views here.
class OrderingFilter(filters.OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        order_by = request.query_params.get(self.ordering_param)
        return queryset.order_by('-created_at') 

class SuggestionViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        mixins.DestroyModelMixin
                    ):
    queryset = Suggestion.objects.all()
    pagination_class = SuggestionPagination
    filter_backends = [OrderingFilter]

    def get_serializer_class(self):
        if self.action == "list":
            return SuggestionSerializer
        elif self.action == "create":
            return SuggestionCreateSerailizer
        return SuggestionDetailSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        elif self.action == "create":
            return [IsAuthenticated()]
        return [IsOwnerOrReadOnly()]
    
    def perform_create(self, serializer):
        serializer.save(writer = self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "건의사항이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

class CommentViewSet(
    viewsets.GenericViewSet, 
    mixins.RetrieveModelMixin, 
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
    ):
    queryset = SuggestionComment.objects.all()
    serializer_class = SuggestionCommentSerializer
    def get_permissions(self):
        if self.action == "retrieve":
            return [AllowAny()]
        return [IsAdminUser()]
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "댓글이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

class SuggestionCommentViewSet(
    viewsets.GenericViewSet, 
    mixins.CreateModelMixin
    ):
    serializer_class = SuggestionCommentSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        suggestion = self.kwargs.get("suggestion_id")
        queryset = SuggestionComment.objects.filter(suggestion_id=suggestion)
        return queryset

    def create(self, request, suggestion_id=None):
        suggestion = get_object_or_404(Suggestion, id=suggestion_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(suggestion=suggestion)
        return Response(serializer.data)
    
class CommentListViewSet(
    viewsets.GenericViewSet, 
    mixins.ListModelMixin
    ):
    serializer_class = SuggestionCommentSerializer
    permission_classes = [AllowAny]
    filter_backends = [OrderingFilter]

    def get_queryset(self):
        suggestion = self.kwargs.get("suggestion_id")
        queryset = SuggestionComment.objects.filter(suggestion_id=suggestion)
        return queryset