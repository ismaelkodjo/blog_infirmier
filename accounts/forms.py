"""
Formulaires pour la gestion des comptes utilisateurs.
Sans dépendance crispy_forms pour compatibilité maximale.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from .models import Profile


class CustomLoginForm(AuthenticationForm):
    """Formulaire de connexion."""
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'placeholder': "Nom d'utilisateur", 'class': 'form-control form-control-lg', 'autofocus': True})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'placeholder': "Mot de passe", 'class': 'form-control form-control-lg'})
    )


class RegisterForm(UserCreationForm):
    """Formulaire d'inscription."""
    first_name = forms.CharField(max_length=30, required=True, label="Prénom",
        widget=forms.TextInput(attrs={'placeholder': 'Prénom', 'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, label="Nom",
        widget=forms.TextInput(attrs={'placeholder': 'Nom', 'class': 'form-control'}))
    email = forms.EmailField(required=True, label="Email",
        widget=forms.EmailInput(attrs={'placeholder': 'votre@email.com', 'class': 'form-control'}))
    password1 = forms.CharField(label="Mot de passe",
        widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe (8 car. min.)', 'class': 'form-control'}))
    password2 = forms.CharField(label="Confirmer",
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmer le mot de passe', 'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': "nom_utilisateur", 'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Un compte avec cet email existe déjà.")
        return email


class ProfileUpdateForm(forms.ModelForm):
    """Formulaire de mise à jour du profil."""
    first_name = forms.CharField(max_length=30, required=False, label="Prénom",
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=False, label="Nom",
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Profile
        fields = ('avatar', 'bio', 'phone', 'website', 'linkedin', 'twitter', 'facebook', 'speciality', 'institution')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Présentez-vous...'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+228 00 00 00 00'}),
            'speciality': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Santé Publique...'}),
            'institution': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre institution...'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
