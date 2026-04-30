from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["puesto", "avatar"]
        widgets = {
            "puesto": forms.TextInput(attrs={"class": "input"}),
        }
