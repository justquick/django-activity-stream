Changelog
==========

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
