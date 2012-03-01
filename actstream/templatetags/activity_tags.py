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

def do_activity_follow_label(parser, tokens):
    bits = tokens.contents.split()
    if len(bits) != 4:
        raise TemplateSyntaxError, "Accepted format {% activity_follow_label [instance] [follow_string] [unfollow_string] %}"
    else:
        return DisplayActivityFollowLabel(*bits[1:])

class DisplayActivityFollowUrl(Node):
    def __init__(self, actor):
        self.actor = Variable(actor)

    def render(self, context):
        actor_instance = self.actor.resolve(context)
        content_type = ContentType.objects.get_for_model(actor_instance).pk
        if _is_following_helper(context, actor_instance):
            return reverse('actstream_unfollow', kwargs={'content_type_id': content_type, 'object_id': actor_instance.pk})
        return reverse('actstream_follow', kwargs={'content_type_id': content_type, 'object_id': actor_instance.pk})

def do_activity_follow_url(parser, tokens):
    bits = tokens.contents.split()
    if len(bits) != 2:
        raise TemplateSyntaxError, "Accepted format {% activity_follow_url [instance] %}"
    else:
        return DisplayActivityFollowUrl(bits[1])

@register.simple_tag
def activity_followers_url(instance):
    content_type = ContentType.objects.get_for_model(instance).pk
    return reverse('actstream_followers',
        kwargs={'content_type_id': content_type, 'object_id': instance.pk})


@register.simple_tag
def activity_followers_count(instance):
    return Follow.objects.for_object(instance).count()


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


class DisplayActionLabel(AsNode):

    def render_result(self, context):
        actor_instance = self.args[0].resolve(context)
        try:
            user = Variable("request.user").resolve(context)
        except VariableDoesNotExist:
            user = None
        try:
            if user and user == actor_instance.user:
                result = " your "
            else:
                result = " %s's " % (actor_instance.user.get_full_name() or
                    actor_instance.user.username)
        except ValueError:
            result = ""
        result += actor_instance.get_label()
        return result


class DisplayAction(AsNode):

    def render_result(self, context):
        action_instance = self.args[0].resolve(context)
        templates = [
            'activity/%s/action.html' % action_instance.verb.replace(' ', '_'),
            'activity/action.html',
        ]
        return render_to_string(templates, {'action': action_instance},
            context)


class DisplayActionShort(Node):
    def __init__(self, action, varname=None):
        self.action = Variable(action)
        self.varname = varname

    def render(self, context):
        action_instance = self.args[0].resolve(context)
        templates = [
            'activity/%s/action.html' % action_instance.verb.replace(' ', '_'),
            'activity/action.html',
        ]
        return render_to_string(templates, {'action': action_instance,
            'hide_actor': True}, context)


class DisplayGroupedActions(AsNode):

    def render(self, context):
        actions_instance = self.args[0].resolve(context)
        templates = [
            'activity/%s/action.html' %
                actions_instance.verb.replace(' ', '_'),
            'activity/action.html',
        ]
        return render_to_string(templates, {'actions': actions_instance},
            context)


class UserContentTypeNode(Node):

    def __init__(self, *args):
        self.args = args

    def render(self, context):
        context[self.args[-1]] = ContentType.objects.get_for_model(User)
        return ''


def display_action(parser, token):
    return DisplayAction.handle_token(parser, token)


def display_action_short(parser, token):
    return DisplayActionShort.handle_token(parser, token)


def display_grouped_actions(parser, token):
    return DisplayGroupedActions.handle_token(parser, token)


def action_label(parser, token):
    return DisplayActionLabel.handle_token(parser, token)


# TODO: remove this, it's heinous
def get_user_contenttype(parser, token):
    return UserContentTypeNode(*token.split_contents())

def is_following(user, actor):
    return Follow.objects.is_following(user, actor)

register.filter(is_following)
register.tag(display_action)
register.tag(display_action_short)
register.tag(display_grouped_actions)
register.tag(action_label)
register.tag(get_user_contenttype)
register.tag('activity_follow_url', do_activity_follow_url)
register.tag('activity_follow_label', do_activity_follow_label)
