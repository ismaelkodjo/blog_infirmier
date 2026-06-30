from django import forms
from .models import Adresse, Commande


class AdresseForm(forms.ModelForm):
    class Meta:
        model = Adresse
        fields = ['prenom', 'nom', 'telephone', 'adresse_ligne1', 'adresse_ligne2', 'ville', 'region', 'pays']
        widgets = {
            'prenom':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'nom':           forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'telephone':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+228 XX XX XX XX'}),
            'adresse_ligne1':forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rue, quartier'}),
            'adresse_ligne2':forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Complément (optionnel)'}),
            'ville':         forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ville'}),
            'region':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Région / Prefecture'}),
            'pays':          forms.TextInput(attrs={'class': 'form-control'}),
        }


class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['mode_paiement', 'notes']
        widgets = {
            'mode_paiement': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'notes':         forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                   'placeholder': 'Instructions de livraison, remarques…'}),
        }
