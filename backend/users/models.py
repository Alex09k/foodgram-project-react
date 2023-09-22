from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """модель пользователя"""
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        help_text='Укажите имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        help_text='Укажите фамилию'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='email',
        help_text='Укажите email'
    )
    
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


