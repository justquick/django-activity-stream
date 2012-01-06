from django.template import Variable, Library, Node, TemplateSyntaxError, TemplateDoesNotExist
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from actstream.models import Follow

register = Library()

def is_following(context, instance):
    try:
        user = context['user']
    except KeyError:
        return False
    content_type = ContentType.objects.get_for_model(instance)
    return bool(Follow.objects.filter(content_type=content_type, user=user, object_id=instance.pk).count())

class DisplayActivityFollowLabel(Node):
    def __init__(self, actor, follow, unfollow):
        self.actor = Variable(actor)
        self.follow = follow
        self.unfollow = unfollow

    def render(self, context):
        actor_instance = self.actor.resolve(context)
        if is_following(context, actor_instance):
            return self.follow
        else:
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
        if is_following(context, actor_instance):
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
    return reverse('actstream_followers', kwargs={'content_type_id': content_type, 'object_id': instance.pk})

@register.simple_tag
def activity_followers_count(instance):
    content_type = ContentType.objects.get_for_model(instance).pk
    val = Follow.objects.filter(content_type=content_type, object_id=instance.pk).count()
    return val


class DisplayActionLabel(Node):
    def __init__(self, actor, varname=None):
        self.actor = Variable(actor)
        self.varname = varname

    def render(self, context):
        actor_instance = self.actor.resolve(context)
        try:
            user = Variable("request.user").resolve(context)
        except:
            user = None
        try:
            if user and user == actor_instance.user:
                result=" your "
            else:
                result = " %s's " % (actor_instance.user.get_full_name() or actor_instance.user.username)
        except ValueError:
            result = ""
        result += actor_instance.get_label()
        if self.varname is not None:
            context[self.varname] = result
            return ""
        else:
            return result

class DisplayAction(Node):
    def __init__(self, action, varname=None):
        self.action = Variable(action)
        self.varname = varname

    def render(self, context):
        action_instance = self.action.resolve(context)
        try:
            action_output = render_to_string(('activity/%(verb)s/action.html' % { 'verb':action_instance.verb.replace(' ','_') }),{ 'action':action_instance },context)
        except TemplateDoesNotExist:
            action_output = render_to_string(('activity/action.html'),{ 'action':action_instance },context)
        if self.varname is not None:
            context[self.varname] = action_output
            return ""
        else:
            return action_output

class DisplayActionShort(Node):
    def __init__(self, action, varname=None):
        self.action = Variable(action)
        self.varname = varname

    def render(self, context):
        action_instance = self.action.resolve(context)
        try:
            action_output = render_to_string(('activity/%(verb)s/action.html' % { 'verb':action_instance.verb.replace(' ','_') }),{ 'hide_actor':True, 'action':action_instance },context)
        except TemplateDoesNotExist:
            action_output = render_to_string(('activity/action.html'),{ 'hide_actor':True, 'action':action_instance },context)
        if self.varname is not None:
            context[self.varname] = action_output
            return ""
        else:
            return action_output

class DisplayGroupedActions(Node):
    def __init__(self, actions, varname=None):
        self.actions = Variable(actions)
        self.varname = varname

    def render(self, context):
        actions_instance = self.action.resolve(context)
        try:
            action_output = render_to_string(('activity/%(verb)s/grouped.html' % { 'verb':actions_instance[0].verb }),{ 'actions':actions_instance })
        except TemplateDoesNotExist:
            action_output = render_to_string(('activity/grouped.html'),{ 'actions':actions_instance })
        if self.varname is not None:
            context[self.varname] = action_output
            return ""
        else:
            return action_output

def do_print_action(parser, token):
    bits = token.contents.split()
    if len(bits) > 3:
        if len(bits) != 4:
            raise TemplateSyntaxError, "Accepted formats {% display_action [action] %} or {% display_action [action] as [var] %}"
        if bits[2] != 'as':
            raise TemplateSyntaxError, "Accepted formats {% display_action [action] %} or {% display_action [action] as [var] %}"
        return DisplayAction(bits[1],bits[3])
    else:
        return DisplayAction(bits[1])

def do_print_action_short(parser, token):
    bits = token.contents.split()
    if len(bits) > 3:
        if len(bits) != 4:
            raise TemplateSyntaxError, "Accepted formats {% display_action [action] %} or {% display_action [action] as [var] %}"
        if bits[2] != 'as':
            raise TemplateSyntaxError, "Accepted formats {% display_action [action] %} or {% display_action [action] as [var] %}"
        return DisplayActionShort(bits[1],bits[3])
    else:
        return DisplayActionShort(bits[1])

def do_print_grouped_actions(parser, token):
    bits = token.contents.split()
    if len(bits) > 3:
        if len(bits) != 4:
            raise TemplateSyntaxError, "Accepted formats {% display_grouped_actions [action] %} or {% display_action [action] as [var] %}"
        if bits[2] != 'as':
            raise TemplateSyntaxError, "Accepted formats {% display_grouped_actions [action] %} or {% display_action [action] as [var] %}"
        return DisplayAction(bits[1],bits[3])
    else:
        return DisplayAction(bits[1])

def do_print_action_label(parser, token):
    bits = token.contents.split()
    if len(bits) > 3:
        if len(bits) != 4:
            raise TemplateSyntaxError, "Accepted formats {% action_label [action] %} or {% action_label [action] as [var] %}"
        if bits[2] != 'as':
            raise TemplateSyntaxError, "Accepted formats {% action_label [action] %} or {% action_label [action] as [var] %}"
        return DisplayActionLabel(bits[1],bits[3])
    else:
        return DisplayActionLabel(bits[1])

def do_get_user_contenttype(parser, token):
    return UserContentTypeNode(*token.split_contents())

class UserContentTypeNode(Node):
    def __init__(self, *args):
        self.args = args

    def render(self, context):
        context[self.args[-1]] = ContentType.objects.get_for_model(User)
        return ''

register.tag('activity_follow_label', do_activity_follow_label)
register.tag('activity_follow_url', do_activity_follow_url)
register.tag('display_action', do_print_action)
register.tag('display_action_short', do_print_action_short)
register.tag('display_grouped_actions', do_print_grouped_actions)
register.tag('action_label', do_print_action_label)
register.tag('get_user_contenttype', do_get_user_contenttype)
