from recipes.models import IngredientRecipe


def representation(context, instance, serializer):
    request = context.get('request')
    new_context = {'request': request}
    return serializer(instance, context=new_context).data


def get_shopping_list(user):
    ingredients = IngredientRecipe.objects.filter(
        recipe__shopping_cart__user=user.user
    )
    compressed_ingredients = {}
    for ing in ingredients:
        compressed_ingredients[
            (ing.ingredient.name, ing.ingredient.measurement_unit)
        ] += ing.amount
    return ([
        f"- {name}: {amount} {measurement_unit}\n"
        for (name, measurement_unit), amount
        in compressed_ingredients.items()
    ])
