from django.forms import ModelForm
from django.utils import timezone
from django import forms

from .models import Post, Profile


class PostForm(ModelForm):
    publish_flg = forms.BooleanField(required=False, label="publish", initial=True)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author'].initial = user

    class Meta:
        model = Post
        fields = ['author', 'create_date', 'title', 'text', 'publish_flg']
        widgets = {'text': forms.Textarea(attrs={'name':'text','rows':15, 'cols':50}),}


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        exclude = ['user']
        widgets = {'text': forms.Textarea(attrs={'name':'text','rows':15, 'cols':100}),}
