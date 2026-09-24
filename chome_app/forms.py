from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile

class SignUpForm(UserCreationForm):
    full_name = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                full_name=self.cleaned_data["full_name"]
            )
        return user
