from django.template import Variable, Library, Node, NodeList, TemplateSyntaxError, TemplateDoesNotExist, VariableDoesNotExist
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from actstream.models import Action
import re



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

class ActivityNodeBase(Node):
    def __init__(self, parser, token):
        '''
        base class for all activity nodes. parses the arguments.
        subclasses should override get_final_result_from_query_set
        to add any further filters.
        '''
        self.object_varname = None
        self.content_type = None
        self.object_id_varname = None
        self.as_varname = self.get_default_var_name()
        r = r'(?P<tag>\w+) for(?: (?P<type>actor|target|action))?(?: (?P<name>[\w\.]+))(?: identified by (?P<id_by>[\w\.]+))?(?: as (?P<as_varname>\w+))?(?: limit(?: to)? (?P<limit>\d+))?'
        p = re.compile(r)
        m = p.match(token.contents)

        if m is None:
            raise TemplateSyntaxError("Your tag doesn't match %s" % r)

        d = m.groupdict()

        if d['type'] is None:
            d['type'] = 'target'

        self.what_to_fetch = d['type']

        if not d['as_varname'] is None:
            self.as_varname = d['as_varname']

        if not d['id_by'] is None:
            self.content_type = ContentType.objects.get(app_label=d['name'].split('.')[0], model=d['name'].split('.')[1])
            self.object_id_varname = d['id_by']
        else:
            self.object_varname = d['name']
       
        if not d['limit'] is None:
            self.limit = d['limit']


    def get_default_var_name(self):
        raise NotImplementedError
    
    def get_final_result_from_query_set(self, qs):
        return qs

    def render_context_value(self, context, context_value):
        return ''
    
    def render(self, context):
        context_value = None
        ctype = None
        c_id = None
        
        if not self.content_type is None:
            ctype = self.content_type
            c_id = Variable(self.object_id_varname).resolve(context)
        else:
            model = Variable(self.object_varname).resolve(context)
            ctype = ContentType.objects.get_for_model(model)
            c_id = model.id
            
        if self.what_to_fetch == 'actor':
            context_value = Action.objects.filter(
                    actor_content_type=ctype,
                    actor_object_id=c_id)
        elif self.what_to_fetch == 'target':
            context_value = Action.objects.filter(
                    target_content_type=ctype,
                    target_object_id=c_id)
        elif self.what_to_fetch == 'action':    
            context_value = Action.objects.filter(
                    action_object_content_type=ctype,
                    action_object_object_id=c_id)

        context_value = self.get_final_result_from_query_set(context_value) 
        context[self.as_varname] = context_value
        return self.render_context_value(context, context_value)

class ActivityCountNode(ActivityNodeBase):
    def get_default_var_name(self):
        return "activity_count"

    def get_final_result_from_query_set(self, queryset):
        return queryset.count()         

class ActivityListNode(ActivityNodeBase):
    def get_default_var_name(self):
        return "activity_list"

    def get_final_result_from_query_set(self, queryset):
        return queryset.all()

class RenderActivityListNode(ActivityListNode):
    def render_context_value(self, context, context_value):
        return render_to_string(('activity/list.html'), {'activity_list' : context_value }, context)



def do_render_activity_list(parser, token):
    '''
    Renders the activities for the specified object
    with the activity/list.html template. see
    get_activity_list for syntax.
    '''
    return RenderActivityListNode(parser, token)

def do_get_activity_list(parser, token):
    '''
    inserts the activities for the requested
    domain object into the specified variable.
    if no variable is specified, then 'activity_list'
    is used.

    Syntax::
        {% get_activity_list for
            (actor|target|action)?
            ( <object> | <app.model> identified by <id> )
            (as <varname>)?
            (limit to <digit>)?
        %}
    Examples::
        {% get_activity_list for actor request.user %}
        {% get_activity_list for target story %}
        {% get_activity_list for target story as al %}
        {% get_activity_list for story limit 5 %}
        {% get_activity_list for target testapp.story identified by 9 as al limit 5 %}
    '''
    return ActivityListNode(parser, token)

def do_get_activity_count(parser, token):
    '''
    Gets the number of activities for the specified object
    see get_activity_list for syntax   
    '''
    return ActivityCountNode(parser, token)


register = Library()     
register.tag('display_action', do_display_action)
register.tag('display_action_short', do_display_action_short)
register.tag('display_grouped_actions', do_display_grouped_actions)
register.tag('action_label', do_print_action_label)
register.tag('get_user_contenttype', do_get_user_contenttype)
register.tag('get_activity_count', do_get_activity_count)
register.tag('get_activity_list', do_get_activity_list)
register.tag('render_activity_list', do_render_activity_list)
