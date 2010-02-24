from actstream.models import Activity, Follow

def actor_stream(actor):
    return Activity.objects.stream_for_actor(actor)
actor_stream.__doc__ = Activity.objects.stream_for_actor.__doc__
    
def user_stream(user):
    return Follow.objects.stream_for_user(user)
user_stream.__doc__ = Follow.objects.stream_for_user.__doc__
    
def model_stream(model):
    return Activity.objects.stream_for_model(model)
model_stream.__doc__ = Activity.objects.stream_for_model.__doc__
