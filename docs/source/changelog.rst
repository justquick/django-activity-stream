Changelog
==========

0.6.0
-----

  - Django 1.8 support
  - Migrated to new migrations framework in Django core
  - Improved db field indexing for models
  - Optional django-generic-admin widgets integration (if installed)
  - Minor templating and unicode fixes
  - Admin displays public flag in list display
  - Improved docs

0.5.1
-----

  - Coverage testing using coveralls.io
  - Feeds refactoring to include JSON and custom feeds
  - Added "any" builtin stream
  - Following method bugfix
  - Register method bugfix
  - Is installed check bugfix
  - Tests for nested app models
  - Moar tests!
  - Added actstream/base.html template for extensibility help


0.5.0
-----

  - Django 1.6 and 1.7 support
  - Python 3 and PyPy support
  - Added new activity_stream templatetag
  - Dropping support for Django<=1.3 and rely on prefetch_related.
  - Added register method for actionable models
  - Dropped support for ACTSTREAM_SETTINGS['MODELS'] setting
  - Added AppConf to support Django>=1.7


0.4.5
-----

  - Django 1.5 support including custom User model
  - Translations and templates install fixes
  - Fixes for MySQL migrations
  - Tox testing for Py 2.6, 2.7 and Django 1.3, 1.4, 1.5
  - Various other bug fixes


0.4.4
-----

  - Added support for custom Action data using JSONField.
  - User of django.timezone.now when available.
  - Templatetag fixes and removal of the follow_label tag.
  - More tests
  - Packaging fixes to include locale & migrations.
  - App settings provided by ACTSTREAM_SETTINGS dictionary.
  - Added following/followers to model accessors and views.

0.4.3
-----

  - Fixed default templatetags to not require auth.User ContentType
  - Added actor_url templatetag

0.4.2
-----

  - Query improvement supporting Django 1.4 prefetch_related (falls back to it's own prefetch also for older Django versions)
  - Admin fixes
  - Packaging fixes
  - Templatetag cleanup and documentation

0.4.1
------

 - Templatetag updates
 - Follow anything
 - Test improvements
 - Loads of fixes

0.4.0
-----

- Scalability thanks to GFK lookup to prefetch actor, target & action_object in Action streams
- Limit number models that will be involved in actions
- Automagically adds GenericRelations to actionable models
- Generates Activity Stream 1.0 spec Atom feed
- Deletes orphaned actions when referenced object is deleted
- Custom, developer generated managers and streams
- I18N in unicode representation and through templating
- Sphinx Docs
- Duh, a changelog
