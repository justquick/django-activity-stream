.. _changelog:

Changelog
=========

0.7.0
-----

  - Django 2.0 support
  - Dropped support for Django 1.8, 1.9, and 1.10
  - Removed compatibility shims for Django < 1.11
  - Adjusted URLs for new versions of Django
  - Improved tox and travis configuration
  - Used render function instead of deprecated render_to_response
  - Upgraded package dependencies
  - Improved performance by using subqueries in user stream query
  - Added AbstractAction and AbstractFollow abstract models
  - Added swappable Action and Follow models

0.6.5
-----

  - Dropped support for Django 1.7
  - Dropped support for Python 3.3
  - Come chat with us on Gitter! https://gitter.im/django-activity-stream/Lobby
  - Added licence support monitoring with FOSSA: https://app.fossa.io/projects/git%2Bgithub.com%2Fjustquick%2Fdjango-activity-stream

0.6.4
-----

  - Dropped support for Django 1.4, 1.5 and 1.6
  - Added explicit 'on_delete' arg to ForeignKey field

0.6.3
-----

  - MySQL monkey patch removal
  - Scrutinizer CI integration

0.6.2
-----

  - Proxy Model support
  - Brazilian Portuguese translations
  - Added new migration to remove data field if not being used
  - URL naming changed for actstream_unfollow_all
  - Test fix

0.6.1
-----

  - **Python 3.5 support**
  - **Django 1.9 support**
  - Better AppConf compatibility
  - More gracefully 404 handling in feeds
  - New urlpatterns support
  - Added unfollow_all support view
  - Improved docs

0.6.0
-----

  - **Django 1.8 support**
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

  - **Django 1.6 and 1.7 support**
  - **Python 3 and PyPy support**
  - **Dropped support for Django 1.3 or older**
  - Added new activity_stream templatetag
  - Added register method for actionable models
  - Dropped support for ACTSTREAM_SETTINGS['MODELS'] setting
  - Added AppConf to support Django>=1.7


0.4.5
-----

  - **Django 1.5 support** including custom User model
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
-----

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
