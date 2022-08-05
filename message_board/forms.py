from django import forms
from . import models


class PublicationForm(forms.ModelForm):
      
  class Meta:
    model = models.Publication
    fields = ("title", "message", "is_active", "category", )
    widgets = {
        "message": forms.Textarea(attrs={'placeholder': 'Write here', 'rows': 5, })
    }

class CommentForm(forms.ModelForm):

  class Meta:
    model = models.Comment
    fields = ("message",)
    labels = {
        'message': 'Comment',
    }
    widgets = {
        'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write something...', 'rows': 3, }),
    }

class ReplyForm(forms.ModelForm):
  class Meta:
    model = models.Comment
    fields = {'message',}
    labels = {
      'message': '',
    }
    widgets = {
      'message': forms.Textarea(attrs={'class': 'reply-form', 'placeholder': 'Reply', 'rows': 1, 'cols':85})
    }


class PollOptionForm(forms.ModelForm):

  class Meta():
    model = models.PollOption
    fields = ('option', )
    labels = {
      'option': 'Add/Update Option'
    }
    widgets = {
        'option': forms.TextInput(attrs={'placeholder': 'New Option', }),
    }

  def clean_option(self):
    option = self.cleaned_data.get('option')
    if not option or option == '':
      raise forms.ValidationError('Required field')
    return option

