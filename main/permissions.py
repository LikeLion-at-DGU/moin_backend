from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif not request.user.is_authenticated:
            if 'password' in request.data:
                return obj.tmp_password == request.data['password']
        else:
            return obj.writer == request.user or request.user.is_superuser