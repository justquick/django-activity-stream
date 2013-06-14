from actstream.compat import get_user_model

User = get_user_model()
USER_ORM = "%s.%s" % (User._meta.app_label, User._meta.module_name)
