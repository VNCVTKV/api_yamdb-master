from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.models import User
import re
from django.core.validators import EmailValidator, MinLengthValidator, MaxLengthValidator, RegexValidator


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all()),
                    MinLengthValidator(3),  # Минимальная длина
                    MaxLengthValidator(150), # Максимальная длина, как у Django User
                     RegexValidator(
                regex=r'^[\w.@+-]+$',  # Разрешенные символы
                message='Username может содержать только буквы, цифры и символы @, ., +, -'
            ), ], required=True
    )
    email = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all()), 
                    EmailValidator()], required=True
    )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Используйте другое имя пользователя'
            )
        return value
    
    def validate_email(self, value):
        if len(value) >= 255 or len(value) == 0:
            raise serializers.ValidationError(
                'Используйте другой имайл'
            )
        return value

    class Meta:
        model = User
        fields = ('username', 'email')


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


# class UserSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(
#         validators=[UniqueValidator(queryset=User.objects.all()),
#                     MinLengthValidator(3),  # Минимальная длина
#                     MaxLengthValidator(150), # Максимальная длина, как у Django User
#                      RegexValidator(
#                 regex=r'^[\w.@+-]+$',  # Разрешенные символы
#                 message='Username может содержать только буквы, цифры и символы @, ., +, -'
#             ), ], required=True
#     )
#     email = serializers.CharField(
#         validators=[UniqueValidator(queryset=User.objects.all()), EmailValidator()],
#         required=True
#     )

#     def validate_username(self, value):
#         if len(value) >= 150 or value == 'me':
#             raise serializers.ValidationError(
#                 'Используйте другое имя пользователя'
#             )
#         return value

#     def validate_email(self, value):
#         if len(value) >= 255 or len(value) == 0:
#             raise serializers.ValidationError(
#                 'Используйте другой имайл'
#             )


#     class Meta:
#         model = User
#         fields = ('username', 'email', 'first_name',
#                   'last_name', 'bio', 'role')
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username',
            'bio', 'email', 'role',
        )