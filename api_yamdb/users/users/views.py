from http.client import BAD_REQUEST, OK

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken


from users.models import User
from users.users.serializers import (SignUpSerializer, TokenSerializer,
                                     UserSerializer)
from users.utils.permissions import IsAdmin
from users.utils.httpmethod import HTTPMethod
from django.core.exceptions import ObjectDoesNotExist



@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def signup(request):
    try:
        user = User.objects.get(username=request.data.get('username',None),
                                email=request.data.get('email', None))
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
                    subject="Регистрация на YamDB",
                    message=f"Код для токена: {confirmation_code}",
                    from_email=None,
                    recipient_list=[user.email],
                )
        return Response({'username': str(user.username),
                                  'email': str(user.email)}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(username=request.data.get('username',None),
                                email=request.data.get('email', None))
            confirmation_code = default_token_generator.make_token(user)
            send_mail(
                    subject="Регистрация на YamDB",
                    message=f"Код для токена: {confirmation_code}",
                    from_email=None,
                    recipient_list=[user.email],
                )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def token_jwt(request):
    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid():
        user = get_object_or_404(
            User,
            username=serializer.validated_data["username"]
        )
        if default_token_generator.check_token(
            user, serializer.validated_data["confirmation_code"]
        ):
            token = AccessToken.for_user(user)
            return Response({"token": str(token)}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['username', ]
    lookup_field = 'username'
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Валидация данных
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        username = request.data.get('username')
        if username == 'me':
            return Response({'error': "Username cannot be 'me'."}, status=status.HTTP_400_BAD_REQUEST)
        return super().partial_update(request, *args, **kwargs)

    @action(detail=False,
            methods=["GET", "PATCH",],
            permission_classes=[IsAuthenticated,])
    def me(self, request):
        serializer = UserSerializer(request.user,
                                    data=request.data,
                                    partial=True)
        if request.user.role == 'admin' or request.user.role == 'moderator':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=OK)
        serializer.is_valid(raise_exception=True)
        serializer.save(role='user')
        return Response(serializer.data, status=OK)