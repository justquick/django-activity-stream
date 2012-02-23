from django.contrib import admin
from actstream import models


class ActionAdmin(admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    list_display = ('__unicode__', 'actor', 'verb', 'target')
    list_editable = ('verb',)
    list_filter = ('timestamp',)
    raw_id_fields = ('actor_content_type','target_content_type',
                     'action_object_content_type')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'user', 'actor')
    list_editable = ('user',)
    list_filter = ('user',)
    raw_id_fields = ('user', 'content_type')


admin.site.register(models.Action, ActionAdmin)
admin.site.register(models.Follow, FollowAdmin)
