from django.db import models 
from django.contrib.auth import get_user_model
from django.db.models.deletion import CASCADE

from colorfield.fields import ColorField
from django.core.validators import MinValueValidator


User = get_user_model()


class Recipe(models.Model):
    """Модель рецепта"""
    author = models.ForeignKey(User, related_name = 'recipes', on_delete=CASCADE,
                               verbose_name='Автор')

    name = models.CharField(max_length=100,
                            unique=True,
                            verbose_name='Название рецепта')
    image = models.ImageField(upload_to='recipe_images/',
                              blank=True,
                              verbose_name='Фото',
                              )
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField('Ingredient',
                                         through='IngredientIntermediate',
                                         verbose_name='Ингридиенты')
    tags = models.ManyToManyField('Tag', related_name='recipes',
                                  verbose_name='Теги')
    Cooking_time = models.IntegerField(verbose_name='Время приготовления')
    

    
    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

class Tag(models.Model):
    """Модель тега"""
    name = models.CharField(max_length=30,
                           unique=True,
                           verbose_name='Тег')
    color = ColorField(max_length=7,
                       unique=True,
                     verbose_name='Цвет тега',)
    slug = models.SlugField(max_length=100, unique=True,
                            verbose_name='Слаг тега')
    
    def __str__(self):
        return f'{self.name}'
    

class Ingredient(models.Model):
    """Модель ингридиентов"""
    name = models.CharField(max_length=100, verbose_name='Ингридиент')
    units = models.CharField(max_length=200,
                            verbose_name='Единица измерения')
    

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)


class IngredientIntermediate(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='ingredient_intermediate',
                                   verbose_name='Рецепт')
    amount = models.PositiveSmallIntegerField('Количество',
                                              validators=[MinValueValidator(1, message='Минимальное количество 1!')]
                                              )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='ingredient_intermediate', 
                               verbose_name='Рецепт')
    

    def __str__(self):
        return (
            f'{self.ingredient.name} ({self.ingredient.units}) - {self.amount} '
        )
    
    class Meta:
        verbose_name = 'Содержание ингредиента'
        verbose_name_plural = 'Содержание ингредиентов'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'amount',),
                name='unique_ingredient_amount',
            ),
        )


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=CASCADE,
                             related_name='follower',
                             verbose_name='Пользователь')
    author = models.ForeignKey(User, on_delete=CASCADE,
                               related_name='following',
                               verbose_name='Автор')
    
    class Meta:
        verbose_name_plural = 'Подписки'
        verbose_name = 'Подписка'
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name='unique_members')]

    def __str__(self):
        return f'{self.user} подписался на {self.author}'
    




