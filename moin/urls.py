"""
URL configuration for moin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

from .utils import upload_image

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('user.urls')),
    path('api/v1/auth/', include('dj_rest_auth.urls')),
    #path('api/v1/auth/', include('dj_rest_auth.registration.urls')),
    #path('api/v1/auth/', include('allauth.urls')),
    path('api/v1/', include('main.urls')),
    path('api/v1/', include('notice.urls')),
    path('api/v1/', include('suggestion.urls')),
    path('api/v1/', include('community.urls')),

    path('api/v1/upload-image', upload_image, name='upload-image')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)