from django import forms
from .models import TagPost, Game, Comments


class AddPostForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['title', 'price', 'content', 'is_published', 'image', 'tags']


class UploadFileForm(forms.Form):
    image = forms.ImageField(label='Файл')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['text_comment']
