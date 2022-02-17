.. _concepts:

Activity Stream Concepts
========================

The terminiology used in this app is based from the `Activity Streams Specification <http://activitystrea.ms/>`_.
The app currently supports the `version 1.0 <http://activitystrea.ms/specs/atom/1.0/>`_ terminology.

Introduction
------------

`<http://activitystrea.ms/specs/json/1.0/#introduction>`_

In its simplest form, an activity consists of an actor, a verb, an object, and a target. It tells the story of a person performing an action on or with an object -- "Geraldine posted a photo to her album" or "John shared a video". In most cases these components will be explicit, but they may also be implied.

It is a goal of this specification to provide sufficient metadata about an activity such that a consumer of the data can present it to a user in a rich human-friendly format. This may include constructing readable sentences about the activity that occurred, visual representations of the activity, or combining similar activities for display.

The basic properties that comprise the description of an activity are defined in the following sections.

Within this specification, an object is a thing, real or imaginary, which participates in an activity. It may be the entity performing the activity, or the entity on which the activity was performed. An object consists of properties defined in the following sections. Certain object types may further refine the meaning of these properties, or they may define additional properties.


Definitions
-----------

Activities are defined by four main components. Here are their definitions from the specification.

 * ``Actor``. The object that performed the activity.

   An ``Object Construct`` that identifies the entity that performed the activity.
   An Activity construct **MUST** have exactly one actor.

 * ``Verb``. The verb phrase that identifies the action of the activity.

   An IRI reference that identifies the action of the activity.
   This value **MUST** be an absolute IRI, or a IRI relative to the base IRI of `<http://activitystrea.ms/schema/1.0/>`_.
   An Activity construct **MUST** have exactly one verb.

 * ``Action Object``. *(Optional)* The object linked to the action itself.

   This ``Object Construct`` identifies the primary object of the activity.
   An Activity construct **MUST** have exactly one object.

 * ``Target``. *(Optional)* The object to which the activity was performed.

   The target of an activity is an ``Object Construct`` that represents the object to which the activity was performed.
   The exact meaning of an activity's target is dependent on the verb of the activity, but will often be the object of the English preposition "to".
   For example, in the activity "John saved a movie to his wishlist", the target of the activity is "wishlist".
   The activity target **MUST NOT** be used to identify an indirect object that is not a target of the activity.
   An Activity construct **MAY** have a target but it **MUST** NOT have more than one.


``Actor``, ``Action Object`` and ``Target`` are all ``Object Constructs`` which are defined as

  An ``Object Construct`` is a thing, real or imaginary, which participates in an activity.
  It may be the entity performing the activity, or the entity on which the activity was performed.
  An object consists of the logical components defined in the following sections.
  Certain object types may further refine the meaning of these components, or they may define additional components.
  If an object type defines an additional component then it **SHOULD** also define the representation of that component in one or more serialization formats.


Example
-------

`justquick <https://github.com/justquick/>`_ ``(actor)`` *closed* ``(verb)`` `issue 2 <https://github.com/justquick/django-activity-stream/issues/2>`_ ``(object)`` on `django-activity-stream <https://github.com/justquick/django-activity-stream/>`_ ``(target)`` 12 hours ago
