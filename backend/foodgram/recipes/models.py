from django.db import models 
from django.contrib.auth import get_user_model
from django.db.models.deletion import CASCADE
from django.db.models import DateTimeField
from colorfield.fields import ColorField


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
    Cooking_time = models.ImageField(verbose_name='Время приготовления')
    pub_date = DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    
    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.text[:15]

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
    Units = models.CharField(max_length=200,
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
    amount = models.IntegerField(verbose_name='Количество')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='ingredient_contained', 
                               verbose_name='Рецепт')
    

    def __str__(self):
        return (f'Ингредиент {self.ingredient.name}'
                f'в рецепте {self.recipe.name}')
    
    class Meta:
        verbose_name = 'Содержание ингредиента'
        verbose_name_plural = 'Содержание ингредиентов'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'amount',),
                name='unique_ingredient_amount',
            ),
        )
    






