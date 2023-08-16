from rest_framework import viewsets, filters
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer, NotificationDetailSerializer
from .paginations import NotificationPagination

# 유저용 - list, detail      
class OrderingFilter(filters.OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        order_by = request.query_params.get(self.ordering_param)
        return queryset.order_by('-updated_at') 
    
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = [OrderingFilter]
    pagination_class = NotificationPagination
    queryset = Notification.objects.all()
    
    def get_serializer_class(self):
        if self.action == "list":
            return NotificationSerializer
        return NotificationDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_cnt += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)