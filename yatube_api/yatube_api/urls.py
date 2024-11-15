from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from api.views import (PostViewSet,
                       CommentViewSet,
                       GroupViewSet)

router = DefaultRouter()
router.register('posts', PostViewSet)
# router.register('posts', PostDetailViewSet)
router.register(r'posts/(?P<post_id>\d+)/comments',
                CommentViewSet,
                basename='post-comments')
router.register(r'groups', GroupViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    # path('api/v1/', include('api.urls')),
    path('api/v1/api-token-auth/',
         obtain_auth_token,
         name='obtain_auth_token'),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
