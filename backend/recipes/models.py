from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models import DateTimeField

from colorfield.fields import ColorField
from django.core.validators import MinValueValidator

from foodgram.constants import NUMBER_SYMBOLS, NUMBER_SYMBOL_FOR_COLORS

from rest_framework.exceptions import ValidationError

from users.models import CustomUser


# def validate_M2M(value):
#     if not value.exists():
#         raise ValidationError('Поле не должно быть пусым!')


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(CustomUser, on_delete=CASCADE,
                               related_name='recipes',
                               verbose_name='Автор')
    name = models.CharField(max_length=NUMBER_SYMBOLS,
                            unique=True,
                            verbose_name='Название рецепта',
                            help_text='Введите название рецепта',)
    image = models.ImageField(upload_to='recipe_images/',
                              blank=True,
                              verbose_name='Фото',
                              help_text='Загрузите фото',
                              )
    text = models.TextField(verbose_name='Описание',
                            help_text='Введите описание рецепта',)
    ingredients = models.ManyToManyField('Ingredient',
                                         through='IngredientRecipe',
                                         verbose_name='Ингридиенты',
                                         help_text='Перечислите ингредиенты',)
    tags = models.ManyToManyField('Tag', related_name='recipes',
                                  verbose_name='Теги')
    cooking_time = models.IntegerField(validators=[MinValueValidator(
        1, 'Количество должно превышать 0',
    )],
        verbose_name='Время приготовления',
        help_text='Укажите время приготовления',)
    pub_date = DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(max_length=NUMBER_SYMBOLS,
                            unique=True,
                            verbose_name='Тег')
    color = ColorField(max_length=NUMBER_SYMBOL_FOR_COLORS,
                       unique=True,
                       verbose_name='Цвет тега',)
    slug = models.SlugField(max_length=NUMBER_SYMBOLS, unique=True,
                            verbose_name='Слаг тега')

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    """Модель ингридиентов."""

    name = models.CharField(max_length=NUMBER_SYMBOLS, verbose_name='Ингридиент',
                            help_text='Введите ингредиент',
                            )
    measurement_unit = models.CharField(max_length=NUMBER_SYMBOLS,
                                        verbose_name='Единица измерения',
                                        help_text='Введите единицу измерения',
                                        )
    
    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit',),
                name='unique_name_measurement_unit',
            ),
        )

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='ingredient_recipe',
                                   verbose_name='Ингредиент')
    amount = models.PositiveSmallIntegerField(
        'Количество', validators=[MinValueValidator(
            1, message='Минимальное количество 1!')])
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='ingredient_recipe',
                               verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Содержание ингредиента'
        verbose_name_plural = 'Содержание ингредиентов'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'amount',),
                name='unique_ingredient_amount',
            ),
        )

    def __str__(self):
        return (
            f'{self.ingredient.name} ({self.ingredient.measurement_unit})'
            f' - {self.amount} '
        )


class Follow(models.Model):
    """"Модель подписки."""
    user = models.ForeignKey(CustomUser,
                             on_delete=CASCADE,
                             related_name='follower',
                             verbose_name='Подписчик',
                             help_text='Подписчик на автора рецепта')
    author = models.ForeignKey(CustomUser, on_delete=CASCADE,
                               related_name='followed',
                               verbose_name='Автор',
                               help_text='Автор рецепта')

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['author', 'user'],
            name='unique_object'
        )]

    def __str__(self):
        return f'{self.user} подписался на {self.author}'
    
    def save(self, **kwargs):
        if self.user == self.author:
            raise ValidationError("Невозможно подписаться на себя")
        super().save()

    
    

class Favorite(models.Model):
    """Модель избранное."""

    user = models.ForeignKey(CustomUser, on_delete=CASCADE,
                             related_name='favorites',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=CASCADE,
                               related_name='favorites',
                               verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'], name='unique_favourite')
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'


class ShoppingCart(models.Model):
    """Модель корзины."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_cart',
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
