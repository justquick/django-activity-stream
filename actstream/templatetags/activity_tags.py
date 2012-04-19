from django.template import Variable, Library, Node, TemplateSyntaxError,\
    VariableDoesNotExist
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from actstream.models import Follow

register = Library()


def _is_following_helper(context, actor):
    return Follow.objects.is_following(context.get('user'), actor)

class DisplayActivityFollowLabel(Node):
    def __init__(self, actor, follow, unfollow):
        self.actor = Variable(actor)
        self.follow = follow
        self.unfollow = unfollow

    def render(self, context):
        actor_instance = self.actor.resolve(context)
        if _is_following_helper(context, actor_instance):
            return self.follow
        return self.unfollow

class DisplayActivityFollowUrl(Node):
    def __init__(self, actor):
        self.actor = Variable(actor)

    def render(self, context):
        actor_instance = self.actor.resolve(context)
        content_type = ContentType.objects.get_for_model(actor_instance).pk
        if _is_following_helper(context, actor_instance):
            return reverse('actstream_unfollow', kwargs={'content_type_id': content_type, 'object_id': actor_instance.pk})
        return reverse('actstream_follow', kwargs={'content_type_id': content_type, 'object_id': actor_instance.pk})

class AsNode(Node):
    """
    Base template Node class for template tags that takes a predefined number
    of arguments, ending in an optional 'as var' section.
    """
    args_count = 1

    @classmethod
    def handle_token(cls, parser, token):
        """
        Class method to parse and return a Node.
        """
        bits = token.contents.split()
        args_count = len(bits) - 1
        if args_count >= 2 and bits[-2] == 'as':
            as_var = bits[-1]
            args_count -= 2
        else:
            as_var = None
        if args_count != cls.args_count:
            arg_list = ' '.join(['[arg]' * cls.args_count])
            raise TemplateSyntaxError("Accepted formats {%% %(tagname)s "
                "%(args)s %%} or {%% %(tagname)s %(args)s as [var] %%}" %
                {'tagname': bits[0], 'args': arg_list})
        args = [parser.compile_filter(token) for token in
            bits[1:args_count + 1]]
        return cls(args, varname=as_var)

    def __init__(self, args, varname=None):
        self.args = args
        self.varname = varname

    def render(self, context):
        result = self.render_result(context)
        if self.varname is not None:
            context[self.varname] = result
            return ''
        return result

    def render_result(self, context):
        raise NotImplementedError("Must be implemented by a subclass")


class DisplayAction(AsNode):

    def render_result(self, context):
        action_instance = self.args[0].resolve(context)
        templates = [
            'activity/%s/action.html' % action_instance.verb.replace(' ', '_'),
            'activity/action.html',
        ]
        return render_to_string(templates, {'action': action_instance},
            context)


class UserContentTypeNode(Node):

    def __init__(self, *args):
        self.args = args

    def render(self, context):
        context[self.args[-1]] = ContentType.objects.get_for_model(User)
        return ''

def display_action(parser, token):
    """
    Renders the template for the action description

    Example::

        {% display_action action %}
    """
    return DisplayAction.handle_token(parser, token)

def is_following(user, actor):
    """
    Returns true if the given user is following the actor

    Example::

        {% if request.user|is_following:another_user %}
            You are already following {{ another_user }}
        {% endif %}
    """
    return Follow.objects.is_following(user, actor)


def follow_url(parser, tokens):
    """
    Renders the URL of the follow view for a particular actor instance

    Example::

        <a href="{% activity_follow_url user %}">{% actstream_follow_label user 'follow' 'stop following' %}</a>

    """
    bits = tokens.contents.split()
    if len(bits) != 2:
        raise TemplateSyntaxError, "Accepted format {% activity_follow_url [instance] %}"
    else:
        return DisplayActivityFollowUrl(bits[1])


def follow_label(parser, tokens):
    """
    Renders the label for following/unfollowing for a particular actor instance

    Example::

        <a href="{% activity_follow_url user %}">{% actstream_follow_label user 'follow' 'stop following' %}</a>

    """
    bits = tokens.contents.split()
    if len(bits) != 4:
        raise TemplateSyntaxError, "Accepted format {% activity_follow_label [instance] [follow_string] [unfollow_string] %}"
    else:
        return DisplayActivityFollowLabel(*bits[1:])


register.filter(is_following)
register.tag(display_action)
register.tag(follow_url)
register.tag(follow_label)
