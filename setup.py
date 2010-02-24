from distutils.core import setup


setup(name='django-activity-stream',
      version='0.1',
      description='Create activities from your site\'s actions',
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
