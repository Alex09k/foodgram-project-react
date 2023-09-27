def representation(context, instance, serializer):
    request = context.get('request')
    new_context = {'request': request}
    return serializer(instance, context=new_context).data