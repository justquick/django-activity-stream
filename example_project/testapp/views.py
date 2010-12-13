from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from testapp.models import Story

# Create your views here.
def stories(request):
    stories = Story.objects.all()
    return render_to_response('stories/list.html', locals())

def story(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    return render_to_response('stories/story.html', locals())

    