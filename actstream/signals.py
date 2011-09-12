from django.dispatch import Signal

action = Signal(providing_args=['actor','verb','verb_uri_prefix',
                                'action_object','target','description',
                                'timestamp'])