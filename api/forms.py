from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
from .models import Bid

class EmailUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        item = self.instance.item

        if amount < item.current_price + 10:
            raise forms.ValidationError("The bid must be at least 10 units higher than the current bid.")

        return amount






