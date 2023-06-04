from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    email = models.EmailField(
        validators=(UnicodeUsernameValidator(),),
        blank=True,
        max_length=settings.LENG_EMAIL,
        unique=True,
        help_text=(f'Длина.{settings.LENG_EMAIL}'
                   f' символов, только слова, цифры и  @/./+/-/_ .'),
        error_messages={
            'unique': ("с таким email есть пользователь"),
        },
        verbose_name='email',
    )
    username = models.CharField(
        validators=(UnicodeUsernameValidator(),),
        blank=True,
        max_length=settings.LENG_USERNAME,
        unique=True,
        help_text=(f'Длина.{settings.LENG_USERNAME}'
                   f' символов, только слова, цифры и  @/./+/-/_ .'),
        error_messages={
            'unique': ("Пользователь с таким именем уже существует"),
        },
        verbose_name="Логин"
    )

    first_name = models.CharField(
        blank=True,
        max_length=settings.LENG_FIRST_NAME,
        help_text=(f'Длина.{settings.LENG_USERNAME}'
                   f' символов, только слова, цифры и  @/./+/-/_ .'),
        verbose_name='Имя',
    )

    last_name = models.CharField(
        blank=True,
        max_length=settings.LENG_LAST_NAME,
        help_text=(f'Длина.{settings.LENG_USERNAME}'
                   f' символов, только слова, цифры и  @/./+/-/_ .'),
        verbose_name='Фамилия',
    )

    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_username_email',
            )
        ]

    def __str__(self):
        return (f'{self.username}, {self.email}'
                f'{self.first_name}, {self.last_name}')


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='subscriber'
    )
    author = models.ForeignKey(
        User,
        related_name='subscibe',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Мои подписки'
        verbose_name_plural = 'Мои подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'user'),
                name='unique_subscribe',
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='\nNo self sibscription\n'
            )
        )

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
