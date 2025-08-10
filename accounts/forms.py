from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.utils.translation import gettext_lazy as _

from manager.models import MyUser


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = MyUser
        fields = ['first_name', 'last_name', 'username', 'email', 'about']
        labels = {
            'first_name': _("Ism"),
            'last_name': _("Familiya"),
            'username': _("Foydalanuvchi nomi"),
            'email': _("Elektron pochta"),
            'about': _("Tarjimayi hol")
        }

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': "form-control"
            }),
            'last_name': forms.TextInput(attrs={
                'class': "form-control"
            }),
            'username': forms.TextInput(attrs={
                'class': "form-control"
            }),
            'email': forms.EmailInput(attrs={
                'class': "form-control"
            }),
            'about': forms.Textarea(attrs={
                'class': "form-control",
                'rows': 3
            })
        }


class AvatarUpdateForm(forms.ModelForm):
    class Meta:
        model = MyUser
        fields = ['avatar']
        labels = {
            'avatar': ""
        }
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': "form-control",
                'accept': "image/*"
            })
        }


class PasswordForm(PasswordChangeForm):
    class Meta:
        model = MyUser

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        old_password = self.fields['old_password']
        new_password1 = self.fields['new_password1']
        new_password2 = self.fields['new_password2']

        old_password.label = _("Amaldagi parol")
        old_password.widget.attrs.update({'class': "form-control"})
        new_password1.widget.attrs.update({'class': "form-control"})
        new_password2.widget.attrs.update({'class': "form-control"})
