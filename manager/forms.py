from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Article, Comment


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if not data and not self.required:
            return []

        if not isinstance(data, (list, tuple)):
            data = [data]

        cleaned_data = []
        errors = []
        for file in data:
            try:
                cleaned_file = super().clean(file, initial)
                cleaned_data.append(cleaned_file)
            except forms.ValidationError as e:
                errors.extend(e.error_list)

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ['user', 'article']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': "form-control",
                'placeholder': _("Izohingizni yozing..."),
                'rows': 3
            })
        }
        labels = {
            'content': _("Izohingiz:")
        }


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content']
        labels = {
            'title': _("Sarlavha"),
            'content': _("Maqola matni")
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3
            })
        }


class ArticleImageForm(forms.Form):
    images = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={
            'accept': 'image/*',
        }),
        label=_("Rasmlar (ixtiyoriy)")
    )
    delete_images = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label=_("O‘chirish uchun rasmlarni tanlang")
    )

    def __init__(self, *args, **kwargs):
        article = kwargs.pop('article', None)
        super().__init__(*args, **kwargs)

        if article:
            self.fields['delete_images'].choices = [
                (str(image.id), image.image.url.split('/')[-1])
                for image in article.images.all()
            ]
