from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """модель пользователя"""
    first_name = models.CharField(max_length=50,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=50,
                                  verbose_name='Фамилия')
    email = models.EmailField(max_length=100,
                              unique=True,
                              verbose_name='email')
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username
