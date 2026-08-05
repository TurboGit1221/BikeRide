from django import forms
from django.contrib.auth.models import User
from .models import ContactMessage

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Potwierdź hasło")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Hasła nie pasują do siebie!")

        return cleaned_data

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username',)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = "Hasło musi zawierać co najmniej 8 znaków."
        self.fields['password2'].help_text = "Wprowadź ponownie hasło."


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ('name', 'email', 'subject', 'message')
        labels = {
            'name': 'Imię',
            'email': 'Adres e-mail',
            'subject': 'Temat',
            'message': 'Wiadomość',
        }
        widgets = {'message': forms.Textarea(attrs={'rows': 5})}
