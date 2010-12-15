from django.template import Node, NodeList, Variable, TemplateSyntaxError, Library
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from actstream.models import Follow
import re

class FollowerNodeBase(Node):
    def __init__(self, parser, token):
        self.object_varname = None
        self.content_type = None
        self.object_id_varname = None
        self.as_varname = self.get_default_var_name()
        r = r'(?P<tag>\w+) for (?P<name>[\w\.]+)(?: identified by (?P<id_by>[\w\.]+))?(?: as (?P<as_varname>\w+))?(?: limit(?: to)? (?P<limit>\d+))?'
        p = re.compile(r)
        m = p.match(token.contents)
        if m is None:
            raise TemplateSyntaxError("Your tag doesn't match %s" % r)
        
        d = m.groupdict()
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
        
        context_value = Follow.objects.filter(
                content_type=ctype,
                object_id=c_id)
        context_value = self.get_final_result_from_query_set(context_value) 
        context[self.as_varname] = context_value
        return self.render_context_value(context, context_value)
        


class UrlForObjectNode(FollowerNodeBase):    
    def __init__(self, parser, token):
        self.object_varname = None

        r = r'(?P<tag>\w+) (?P<name>[\w\.]+)'
        p = re.compile(r)
        m = p.match(token.contents)
        if m is None:
            raise TemplateSyntaxError("Your tag doesn't match %s" % r)
        
        d = m.groupdict()
        self.object_varname = d['name']

    def render(self, context):
        model = Variable(self.object_varname).resolve(context)
        return self.render_link(model, context)

    def render_link(self, model, context):
        raise NotImplementedError



class UrlToFollowNode(UrlForObjectNode):    
    def render_link(self, model, context):
        ctype = ContentType.objects.get_for_model(model)
        return reverse('actstream_follow', None, (ctype.pk,model.pk))

class UrlToUnfollowNode(UrlForObjectNode):    
    def render_link(self, model, context):
        ctype = ContentType.objects.get_for_model(model)
        return reverse('actstream_unfollow', None, (ctype.pk,model.pk))



class FollowerCountNode(FollowerNodeBase):
    def get_default_var_name(self):
        return "follower_count"
    
    def get_final_result_from_query_set(self, queryset):
        return queryset.count()         


    
class FollowerListNode(FollowerNodeBase):
    def get_default_var_name(self):
        return "follower_list"

    def get_final_result_from_query_set(self, queryset):
        return queryset.all()



class RenderFollowerListNode(FollowerListNode):
    def render_context_value(self, context, context_value):
        return render_to_string(('follower/list.html'), {'follower_list' : context_value }, context)




class BooleanNode(Node):
    def __init__(self, boolean_function, nodelist_true, nodelist_false):
        self.boolean_function = boolean_function
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
    def render(self, context):
        if self.boolean_function(context):
            return self.nodelist_true.render(context)	
        else:
            return self.nodelist_false.render(context)

def do_if_user_is_following(parser, token):
    bits = token.contents.split()
    if len(bits) != 2:
        raise TemplateSyntaxError, "'if_user_is_following' statement requires one argument [model object]"
    model_object_var = bits[1]
    nodelist_true = parser.parse(('else', 'endif'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endif',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    b = lambda context : Follow.objects.filter(
        user=Variable("request.user").resolve(context), 
        object_id=Variable(model_object_var).resolve(context).pk,
        content_type=ContentType.objects.get_for_model(Variable(model_object_var).resolve(context))
        ).exists() 
    return BooleanNode(b, nodelist_true, nodelist_false)


def do_render_follower_list(parser, token):
    return RenderFollowerListNode(parser, token)

def do_get_follower_list(parser, token):
    return FollowerListNode(parser, token)

def do_get_follower_count(parser, token):
    """
    Gets the number of followers for the specified object or apramters and
    puts the value into the context.  The default variable name is
    'follower_count' but can be altered using the 'as var' syntax.
    
    Syntax::

        {% get_follower_count for [object] as [varname]  %}
        {% get_follower_count for [app].[model] identified by [variable] as [varname] limit [number] %}

    Example usage::

        {% get_follower_count for story %}
        {% get_follower_count for story as fc %}
        {% get_follower_count for tesapp.story story.id as fc %}

    """
    return FollowerCountNode(parser, token)

def do_url_to_follow(parser, token):
    return UrlToFollowNode(parser, token)

def do_url_to_unfollow(parser, token):
    return UrlToUnfollowNode(parser, token)


register = Library()     
register.tag('get_follower_count', do_get_follower_count)
register.tag('get_follower_list', do_get_follower_list)
register.tag('render_follower_list', do_render_follower_list)
register.tag('if_user_is_following', do_if_user_is_following)
register.tag('url_to_follow', do_url_to_follow)
register.tag('url_to_unfollow', do_url_to_unfollow)