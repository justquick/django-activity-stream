from django.template import Variable, Library, Node, TemplateSyntaxError, TemplateDoesNotExist
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


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
                result = " your "
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
            action_output = render_to_string(('activity/%(verb)s/action.html' % { 'verb':action_instance.verb.replace(' ', '_') }), { 'action':action_instance }, context)
        except TemplateDoesNotExist:
            action_output = render_to_string(('activity/action.html'), { 'action':action_instance }, context)
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
            action_output = render_to_string(('activity/%(verb)s/action.html' % { 'verb':action_instance.verb.replace(' ', '_') }), { 'hide_actor':True, 'action':action_instance }, context)
        except TemplateDoesNotExist:
            action_output = render_to_string(('activity/action.html'), { 'hide_actor':True, 'action':action_instance }, context)
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
            action_output = render_to_string(('activity/%(verb)s/grouped.html' % { 'verb':actions_instance[0].verb }), { 'actions':actions_instance })
        except TemplateDoesNotExist:
            action_output = render_to_string(('activity/grouped.html'), { 'actions':actions_instance })
        if self.varname is not None:
            context[self.varname] = action_output
            return ""
        else:
            return action_output        
        
def do_display_action(parser, token):
    """
    Renders an action into html using the :template: 'activity/%(verb)s/action.html' ; *verb* coming
    from the Action (spaces are replaced with underscores) or 'activity/action.html' if the former is not found.
    
    Usage::
    
        {% load activity_tags %}
        {% display_action [action] %}
        .. renders the template inline ..
        
        {% display_action [action] as [var] %}"
        .. renders the template and stores into the content variable [var] ..
        {{ [var] }}
    
    """
    bits = token.contents.split()
    if len(bits) > 3:
        if len(bits) != 4:
            raise TemplateSyntaxError, "Accepted formats {% display_action [action] %} or {% display_action [action] as [var] %}"
        if bits[2] != 'as':
            raise TemplateSyntaxError, "Accepted formats {% display_action [action] %} or {% display_action [action] as [var] %}"
        return DisplayAction(bits[1], bits[3])
    else:
        return DisplayAction(bits[1])
        
def do_display_action_short(parser, token):
    """
    Same as :tag:`display_action` except that it inserts a variable called 'hide_actor' into the context with 
    a value of True
    
    Usage::
    
        {% load activity_tags %}
        {% display_action_short [action] %}
        .. renders the template inline ..

        {% display_action_short [action] as [var] %}"
        .. renders the template and stores into the content variable [var] ..
        {{ [var] }}
    
    """
    bits = token.contents.split()
    if len(bits) > 3:
        if len(bits) != 4:
            raise TemplateSyntaxError, "Accepted formats {% display_action [action] %} or {% display_action [action] as [var] %}"
        if bits[2] != 'as':
            raise TemplateSyntaxError, "Accepted formats {% display_action [action] %} or {% display_action [action] as [var] %}"
        return DisplayActionShort(bits[1], bits[3])
    else:
        return DisplayActionShort(bits[1])
        
def do_display_grouped_actions(parser, token):
    """
    
    Usage::
        {% display_grouped_actions [action] %}
    With 'as var' syntax::
        {% display_grouped_actions [action] as [var] %}
    """
    bits = token.contents.split()
    if len(bits) > 3:
        if len(bits) != 4:
            raise TemplateSyntaxError, "Accepted formats {% display_grouped_actions [action] %} or {% display_grouped_actions [action] as [var] %}"
        if bits[2] != 'as':
            raise TemplateSyntaxError, "Accepted formats {% display_grouped_actions [action] %} or {% display_grouped_actions [action] as [var] %}"
        return DisplayAction(bits[1], bits[3])
    else:
        return DisplayAction(bits[1])
        
def do_print_action_label(parser, token):
    bits = token.contents.split()
    if len(bits) > 3:
        if len(bits) != 4:
            raise TemplateSyntaxError, "Accepted formats {% action_label [action] %} or {% action_label [action] as [var] %}"
        if bits[2] != 'as':
            raise TemplateSyntaxError, "Accepted formats {% action_label [action] %} or {% action_label [action] as [var] %}"
        return DisplayActionLabel(bits[1], bits[3])
    elif len(bits) < 2:
        raise TemplateSyntaxError, "Accepted formats {% action_label [action] %} or {% action_label [action] as [var] %}"
    else:
        return DisplayActionLabel(bits[1])
    
def do_get_user_contenttype(parser, token):
    """
    Sets a context variable that contains the user content type
    object from the content type manager. The default variable name 
    is 'get_user_content_type' unless you use the 'as var' format (see below)
    
    Usage::
    
        {% load activity_tags %}
        {% get_user_content_type %}
        {{ get_user_content_type.id }}
    
    The 'as var' format::
    
        {% get_user_content_type as var %}
        {{ var.id }}
    """
    return UserContentTypeNode(*token.split_contents())

class UserContentTypeNode(Node):
    def __init__(self, *args):
        self.args = args
        
    def render(self, context):
        context[self.args[-1]] = ContentType.objects.get_for_model(User)
        return ''




#get_comment_count
#Gets the comment count for the given params and populates the template context with a variable containing that value, whose name is defined by the 'as' clause.
#{% get_comment_count for [object] as [varname]  %}
#{% get_comment_count for [app].[model] [object_id] as [varname]  %}
#Example usage:
#
#{% get_comment_count for event as comment_count %}
#{% get_comment_count for calendar.event event.id as comment_count %}
#{% get_comment_count for calendar.event 17 as comment_count %}
#
#
#
#get_comment_list
#Gets the list of comments for the given params and populates the template context with a variable containing that value, whose name is defined by the 'as' clause.
#
#Syntax:
#
#{% get_comment_list for [object] as [varname]  %}
#{% get_comment_list for [app].[model] [object_id] as [varname]  %}
#Example usage:
#
#{% get_comment_list for event as comment_list %}
#{% for comment in comment_list %}
#    ...
#{% endfor %}
#get_comment_permalink
#Get the permalink for a comment, optionally specifying the format of the named anchor to be appended to the end of the URL.

#
#render_comment_list
#Render the comment list (as returned by {% get_comment_list %}) through the comments/list.html template
#{% render_comment_list for [object] %}
#{% render_action_list for [app].[model] [object_id] %}
#{% render_action_list for event %}



register = Library()     
register.tag('display_action', do_display_action)
register.tag('display_action_short', do_display_action_short)
register.tag('display_grouped_actions', do_display_grouped_actions)
register.tag('action_label', do_print_action_label)
register.tag('get_user_contenttype', do_get_user_contenttype)
