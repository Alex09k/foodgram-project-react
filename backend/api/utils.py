from recipes.models import (ShoppingCart,
                            IngredientRecipe,
                            Ingredient)

from django.http import FileResponse

def representation(context, instance, serializer):
    request = context.get('request')
    new_context = {'request': request}
    return serializer(instance, context=new_context).data

def get_shopping_list(request):
        user = request.user
        purchases = ShoppingCart.objects.filter(user=user)
        file = 'shopping-list.txt'
        with open(file, 'w') as f:
            shop_cart = dict()
            for purchase in purchases:
                ingredients = IngredientRecipe.objects.filter(
                    recipe=purchase.recipe.id
                )
                for r in ingredients:
                    i = Ingredient.objects.get(pk=r.ingredient.id)
                    point_name = f'{i.name} ({i.measurement_unit})'
                    if point_name in shop_cart.keys():
                        shop_cart[point_name] += r.amount
                    else:
                        shop_cart[point_name] = r.amount
            for name, amount in shop_cart.items():
                f.write(f'* {name} - {amount}\n')
        return FileResponse(open(file, 'rb'), as_attachment=True)
