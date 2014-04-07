from django.utils.translation import ugettext_lazy as _



VERB_WAS_CREATED = _(u'was created')
VERB_SAID = _(u'said')
VERB_KILLED = _(u'killed')
VERB_FOLLOWED = _(u'followed')
VERB_JOINED = _(u'joined')
VERB_STARTED_FOLLOWING = _(u'started following')
VERB_COMMENTED_ON = _(u'commented on')
VERB_RESPONDED_TO = _(u'responded to')
VERB_ENGLISH = _(u'English1')
VERB_CREATED_COMMENT = _(u'created comment')
VERB_ANGLAIS = _(u'Anglais')
#VERB_JOINED = _(u'joined')
#VERB_JOINED = _(u'joined')


VERB_CHOICES =   (     
        (1, VERB_WAS_CREATED),(2, VERB_SAID),(3, VERB_KILLED),(4, VERB_FOLLOWED),
        (5, VERB_JOINED),(6, VERB_STARTED_FOLLOWING),
        (7, VERB_COMMENTED_ON),
        (8, VERB_RESPONDED_TO),
        (9, VERB_ENGLISH),
        (10, VERB_CREATED_COMMENT),
        (11, VERB_ANGLAIS),
#        (7, VERB_COMMENTED_ON),
        )

