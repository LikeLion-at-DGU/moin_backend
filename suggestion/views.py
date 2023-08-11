from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from .models import Suggestion, SuggestionComment, SuggestionImage
from .serializers import SuggestionSerializer, SuggestionCreateSerailizer, SuggestionDetailSerializer, SuggestionCommentSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from .permissions import IsOwnerOrReadOnly

# Create your views here.
class SuggestionViewSet(viewsets.ModelViewSet):
    queryset = Suggestion.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return SuggestionSerializer
        elif self.action == "create":
            return SuggestionCreateSerailizer
        return SuggestionDetailSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsOwnerOrReadOnly()]
    
    def perform_create(self, serializer):
        serializer.save(writer = self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()
        images_data = self.request.data.get('images', [])

        existing_images = instance.images_suggestion.all()

        for image_instance in existing_images:
            image_id = str(image_instance.id)
            image_data = next((data for data in images_data if data.get('id') == image_id), None)
            
            if image_data:
                if image_data.get('DELETE', False):
                    image_instance.delete()
                else:
                    image_instance.image = image_data.get('image')
                    image_instance.save()
            else:
                image_instance.delete()

        # for image_data in images_data:
        #     if 'id' not in image_data:
        #         SuggestionImage.objects.create(suggestion=instance, image=image_data.get('image'))


    
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
    mixins.ListModelMixin, 
    mixins.CreateModelMixin
    ):

    serializer_class = SuggestionCommentSerializer
    def get_permissions(self):
        if self.action == "list":
            return [AllowAny()]
        return [IsAdminUser()]

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