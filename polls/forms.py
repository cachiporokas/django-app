from django.forms.models import inlineformset_factory

from .models import Poll, Choice

PollChoiceFormset = inlineformset_factory(Poll, Choice, fields=('option',))