from distutils.core import setup


setup(name='django-activity-stream',
      version='0.1',
      description='Generate generic activity streams from the actions on your site. Users can follow any actor\'s activities for personalized streams.',
      long_description=open('README.rst').read(),
      author='Justin Quick',
      author_email='justquick@gmail.com',
      url='http://github.com/justquick/django-activity-stream',
      packages=['actstream'],
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
      )
