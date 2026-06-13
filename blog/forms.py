"""
Formulaires du blog — sans crispy_forms.
"""

from django import forms
from .models import Article, Comment, Category


class ArticleForm(forms.ModelForm):
    """Formulaire de création/modification d'article."""

    class Meta:
        model = Article
        fields = [
            'title', 'subtitle', 'summary', 'cover_image',
            'content', 'category', 'tags', 'status',
            'featured', 'allow_comments', 'meta_description', 'meta_keywords'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Titre de l\'article...'}),
            'subtitle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sous-titre...'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': 500, 'placeholder': 'Résumé de l\'article...'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'maxlength': 160}),
            'meta_keywords': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'mot-clé1, mot-clé2...'}),
        }


class CommentForm(forms.ModelForm):
    """Formulaire de commentaire."""

    class Meta:
        model = Comment
        fields = ['author_name', 'author_email', 'content']
        widgets = {
            'author_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}),
            'author_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre email (non publié)'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Votre commentaire...', 'rows': 4}),
        }
        labels = {
            'author_name': 'Nom',
            'author_email': 'Email',
            'content': 'Commentaire',
        }
