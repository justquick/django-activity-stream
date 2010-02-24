from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from actstream.models import Follow, Activity

@login_required
def follow(request, content_type_id, object_id):
    ctype = get_object_or_404(ContentType, pk=content_type_id)
    actor = get_object_or_404(ctype.model_class(), pk=object_id)
    _,created = Follow.objects.get_or_create(user=request.user,
        content_type=ctype, object_id=object_id)
    if request.is_ajax():
        return HttpResponse()
    if 'next' in request.REQUEST:
        return HttpResponseRedirect(request.REQUEST['next'])
    return render_to_response('activity/follow.html', {
            'actor':actor,'created':created
        }, context_instance=RequestContext(request))
    
@login_required
def stream(request):
    return render_to_response('activity/stream.html', {
            'actor':request.user,
            'object_list':Follow.objects.stream(request.user)
        }, context_instance=RequestContext(request))
    
def user(request, username):
    user = get_object_or_404(User, username=username)
    return render_to_response('activity/stream.html', {
            'actor':user,'object_list':Activity.objects.stream(user)
        }, context_instance=RequestContext(request)) 