from django import forms
from django.forms import ModelForm

from comments.models import Comment


class CommentForm(ModelForm):
    post_slug = forms.CharField(
        label="Post ID",
        required=True,
        max_length=54,
        widget=forms.HiddenInput
    )

    block = forms.CharField(
        label="Block ID",
        max_length=54,
        widget=forms.HiddenInput,
        required=False,
    )

    text = forms.CharField(
        label="Text",
        min_length=3,
        max_length=10000,
        required=True,
    )

    class Meta:
        model = Comment
        fields = [
            "block",
            "text",
        ]

