from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets
from rest_framework.pagination import PageNumberPagination
from api.titles.serializers import (CategorySerializer, GenreSerializer,
                                    TitleCreateSerializer, TitleReadSerializer,
                                    ReviewSerializer, CommentSerializer)
from api.utils.mixins import ListCreateDestroyMixin
from api.utils.permissions import  (IsAdminOrReadOnly,
                                    IsAminOrModeratorOrReadOnly)
from api.utils.filters import TitleFilter
from core.models import Category, Genre, Review, Comment, Title
from rest_framework import status


class CategoryViewSet(ListCreateDestroyMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['name', ]
    lookup_field = 'slug'
    pagination_class = PageNumberPagination

    def create(self, request):
        if request.user.role == "user" or request.user.is_anonymous:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().create(request)


class GenreViewSet(ListCreateDestroyMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['name', ]
    lookup_field = 'slug'
    pagination_class = PageNumberPagination

    def create(self, request):
        if request.user.role == "user" or request.user.is_anonymous:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().create(request)    


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.order_by('id').annotate(
        rating=Avg('reviews__score')
    )
    serializer_class = TitleCreateSerializer
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filter_class = TitleFilter
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TitleCreateSerializer
        return TitleReadSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAminOrModeratorOrReadOnly, ]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()
    
    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAminOrModeratorOrReadOnly, ]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        review_id = self.kwargs.get("review_id")
        title_id = self.kwargs.get("title_id")
        review = get_object_or_404(Review, id=review_id, title_id=title_id)
        return review.comments.all()
    
    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get("review_id"), title_id = self.kwargs.get("title_id"))
        serializer.save(author=self.request.user, review=review)