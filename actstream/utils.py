from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured

def get_class(import_path):
    """
    Imports a class from an import path given as string,
    e. g. 'project.module.MyClass'. 

    Adapted from django.core.files.storage.get_storage_class.

    """
    if not import_path:
        raise ValueError('No module import path specified.')
    try:
        dot = import_path.rindex('.')
    except ValueError:
        raise ImproperlyConfigured("%s isn't a valid module." % import_path)
    module, classname = import_path[:dot], import_path[dot+1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing module %s: "%s"' % (module, e))
    try:
        return getattr(mod, classname)
    except AttributeError:
        raise ImproperlyConfigured('The module "%s" does not define a "%s" class.' % (module, classname))
