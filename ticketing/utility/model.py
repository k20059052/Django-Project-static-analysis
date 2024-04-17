def get_model_object(model, **kwargs):
    try:
        object = model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None
    return object


def delete_model_object(model, **kwargs):
    try:
        object = model.objects.get(**kwargs)
        object.delete()
    except model.DoesNotExist:
        return None
