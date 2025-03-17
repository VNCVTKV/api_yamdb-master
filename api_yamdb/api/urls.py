from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.titles.views import (CategoryViewSet, GenreViewSet,
                              TitleViewSet, ReviewViewSet, CommentViewSet)
from users.users.views import UserViewSet, signup, token_jwt


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register('categories', CategoryViewSet)
router.register('titles', TitleViewSet)
router.register('genres', GenreViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', signup, name='signup'),
    path('v1/auth/token/', token_jwt, name='token'),
]
