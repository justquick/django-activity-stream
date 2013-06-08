from distutils.core import setup
from actstream import __version__

setup(name='django-activity-stream',
      version=__version__,
      description='Generate generic activity streams from the actions on your '
            'site. Users can follow any actor\'s activities for personalized '
            'streams.',
      long_description=open('README.rst').read(),
      author='Justin Quick',
      author_email='justquick@gmail.com',
      url='http://github.com/justquick/django-activity-stream',
      packages=['actstream',
                'actstream.migrations',
                'actstream.templatetags',
                'actstream.runtests'],
      package_data={'actstream': ['locale/*/LC_MESSAGES/*.po',
                                 'templates/actstream/*.html']},
      zip_safe=False,
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
      )
