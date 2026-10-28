from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from accounts.models import User


class AccountCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "name")


class AccountChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("email", "name", "first_name", "last_name")
