from django.dispatch import Signal

action = Signal(providing_args=['actor','verb','target','description','timestamp'])