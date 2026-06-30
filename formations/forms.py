from django import forms
from .models import Inscription


class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = ['prenom', 'nom', 'email', 'telephone', 'profession', 'mode_paiement', 'notes_admin']
        widgets = {
            'prenom':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'nom':          forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'email':        forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.com'}),
            'telephone':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+228 XX XX XX XX'}),
            'profession':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Infirmier(e), médecin, étudiant…'}),
            'mode_paiement':forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'notes_admin':  forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                  'placeholder': 'Questions, remarques…'}),
        }
        labels = {
            'notes_admin': 'Questions / remarques',
        }
