"""
Vues pour la gestion des comptes utilisateurs.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from .forms import RegisterForm, CustomLoginForm, ProfileUpdateForm
from .models import Profile


def register_view(request):
    """Vue d'inscription."""
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.first_name} ! Votre compte a été créé avec succès.")
            return redirect('core:home')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form, 'title': 'Inscription'})


def login_view(request):
    """Vue de connexion."""
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bon retour, {user.first_name or user.username} !")
            next_url = request.GET.get('next', 'core:home')
            return redirect(next_url)
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = CustomLoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'title': 'Connexion'})


@login_required
def logout_view(request):
    """Vue de déconnexion."""
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('core:home')


@login_required
def profile_view(request):
    """Vue du profil utilisateur."""
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'title': 'Mon Profil'
    })


@login_required
def profile_edit_view(request):
    """Vue de modification du profil."""
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save()
            # Update user fields
            user = request.user
            user.first_name = form.cleaned_data.get('first_name', '')
            user.last_name = form.cleaned_data.get('last_name', '')
            user.email = form.cleaned_data.get('email', '')
            user.save()
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'accounts/profile_edit.html', {
        'form': form,
        'title': 'Modifier mon profil'
    })


@login_required
def change_password_view(request):
    """Vue de changement de mot de passe."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Votre mot de passe a été modifié avec succès.")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {
        'form': form,
        'title': 'Changer mon mot de passe'
    })


def public_profile_view(request, username):
    """Vue publique du profil d'un auteur."""
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    articles = user.articles.filter(status='published').order_by('-published_at')[:6]
    return render(request, 'accounts/public_profile.html', {
        'profile_user': user,
        'profile': profile,
        'articles': articles,
        'title': f"Profil de {user.get_full_name() or user.username}"
    })
