from django.contrib.contenttypes.models import ContentType
from django.template import Variable, Library, Node, TemplateSyntaxError
from django.template.loader import render_to_string
from django.urls import reverse

from actstream.models import Follow, Action


register = Library()


class DisplayActivityFollowUrl(Node):
    def __init__(self, actor, actor_only=True, flag=''):
        self.actor = Variable(actor)
        self.actor_only = actor_only
        self.flag = flag

    def render(self, context):
        actor_instance = self.actor.resolve(context)
        content_type = ContentType.objects.get_for_model(actor_instance).pk

        kwargs = {
            'content_type_id': content_type,
            'object_id': actor_instance.pk
        }

        if self.flag:
            kwargs['flag'] = self.flag

        if Follow.objects.is_following(context.get('user'), actor_instance, flag=self.flag):
            return reverse('actstream_unfollow', kwargs=kwargs)
        if self.actor_only:
            return reverse('actstream_follow', kwargs=kwargs)
        return reverse('actstream_follow_all', kwargs=kwargs)


class DisplayActivityActorUrl(Node):
    def __init__(self, actor):
        self.actor = Variable(actor)

    def render(self, context):
        actor_instance = self.actor.resolve(context)
        content_type = ContentType.objects.get_for_model(actor_instance).pk
        return reverse('actstream_actor', kwargs={
            'content_type_id': content_type, 'object_id': actor_instance.pk})


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
        tag_error = "Accepted formats {%% %(tagname)s %(args)s %%} or " \
                    "{%% %(tagname)s %(args)s as [var] %%}"
        bits = token.split_contents()
        args_count = len(bits) - 1
        if args_count >= 2 and bits[-2] == 'as':
            as_var = bits[-1]
            args_count -= 2
        else:
            as_var = None
        if args_count != cls.args_count:
            arg_list = ' '.join(['[arg]' * cls.args_count])
            raise TemplateSyntaxError(tag_error % {'tagname': bits[0],
                                                   'args': arg_list})
        args = [parser.compile_filter(tkn)
                for tkn in bits[1:args_count + 1]]
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
        action_instance = context['action'] = self.args[0].resolve(context)
        templates = [
            'actstream/%s/action.html' % action_instance.verb.replace(' ', '_'),
            'actstream/action.html',
        ]
        return render_to_string(templates, context.flatten())


def display_action(parser, token):
    """
    Renders the template for the action description

    ::

        {% display_action action %}
    """
    return DisplayAction.handle_token(parser, token)


def is_following(user, actor):
    """
    Returns true if the given user is following the actor

    ::

        {% if request.user|is_following:another_user %}
            You are already following {{ another_user }}
        {% endif %}
    """
    return Follow.objects.is_following(user, actor)


class IsFollowing(AsNode):
    args_count = 3

    def render_result(self, context):
        user = self.args[0].resolve(context)
        actor = self.args[1].resolve(context)
        flag = self.args[2].resolve(context)

        return Follow.objects.is_following(user, actor, flag=flag)


def is_following_tag(parser, token):
    """
    Returns true if the given user is following the actor marked by a flag, such as 'liking', 'watching' etc..
    You can also save the returned value to a template variable by as syntax.
    If you don't want to specify a flag, pass an empty string or use `is_following` template filter.

    ::

        {% is_following user group "liking" %}
        {% is_following user group "liking" as is_liking %}
        {% is_following user group "" as is_following %}
    """
    return IsFollowing.handle_token(parser, token)


def follow_url(parser, token):
    """
    Renders the URL of the follow view for a particular actor instance

    ::

        <a href="{% follow_url other_user %}">
            {% if request.user|is_following:other_user %}
                stop following
            {% else %}
                follow
            {% endif %}
        </a>

        <a href="{% follow_url other_user 'watching' %}">
            {% is_following user group "watching" as is_watching %}
            {% if is_watching %}
                stop watching
            {% else %}
                watch
            {% endif %}
        </a>
    """
    bits = token.split_contents()

    if len(bits) > 3:
        raise TemplateSyntaxError("Accepted format {% follow_url [instance] %} or {% follow_url [instance] [flag] %}")
    elif len(bits) == 2:
        return DisplayActivityFollowUrl(bits[1])
    else:
        flag = bits[2][1:-1]
        return DisplayActivityFollowUrl(bits[1], flag=flag)


def follow_all_url(parser, token):
    """
    Renders the URL to follow an object as both actor and target

    ::

        <a href="{% follow_all_url other_user %}">
            {% if request.user|is_following:other_user %}
                stop following
            {% else %}
                follow
            {% endif %}
        </a>

        <a href="{% follow_all_url other_user 'watching' %}">
            {% is_following user group "watching" as is_watching %}
            {% if is_watching %}
                stop watching
            {% else %}
                watch
            {% endif %}
        </a>
    """
    bits = token.split_contents()
    if len(bits) > 3:
        raise TemplateSyntaxError(
            "Accepted format {% follow_all_url [instance] %} or {% follow_url [instance] [flag] %}"
        )
    elif len(bits) == 2:
        return DisplayActivityFollowUrl(bits[1], actor_only=False)
    else:
        flag = bits[2][1:-1]
        return DisplayActivityFollowUrl(bits[1], actor_only=False, flag=flag)


def actor_url(parser, token):
    """
    Renders the URL for a particular actor instance

    ::

        <a href="{% actor_url request.user %}">View your actions</a>
        <a href="{% actor_url another_user %}">{{ another_user }}'s actions</a>

    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("Accepted format "
                                  "{% actor_url [actor_instance] %}")
    else:
        return DisplayActivityActorUrl(*bits[1:])


def activity_stream(context, stream_type, *args, **kwargs):
    """
    Renders an activity stream as a list into the template's context.
    Streams loaded by stream_type can be the default ones (eg user, actor, etc.) or a user defined stream.
    Extra args/kwargs are passed into the stream call.

    ::

        {% activity_stream 'actor' user %}
        {% for action in stream %}
            {% display_action action %}
        {% endfor %}
    """
    if stream_type == 'model':
        stream_type = 'model_actions'
    if not hasattr(Action.objects, stream_type):
        raise TemplateSyntaxError('Action manager has no attribute: %s' % stream_type)
    ctxvar = kwargs.pop('as', 'stream')
    context[ctxvar] = getattr(Action.objects, stream_type)(*args, **kwargs)
    return ''


register.filter(activity_stream)
register.filter(is_following)
register.tag(name='is_following', compile_function=is_following_tag)
register.tag(display_action)
register.tag(follow_url)
register.tag(follow_all_url)
register.tag(actor_url)
register.simple_tag(takes_context=True)(activity_stream)
