from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('inscription/', views.register_view, name='register'),
    path('connexion/', views.login_view, name='login'),
    path('deconnexion/', views.logout_view, name='logout'),
    path('profil/', views.profile_view, name='profile'),
    path('profil/modifier/', views.profile_edit_view, name='profile_edit'),
    path('profil/mot-de-passe/', views.change_password_view, name='change_password'),
    path('auteur/<str:username>/', views.public_profile_view, name='public_profile'),

    # Password reset
    path('reinitialiser-mot-de-passe/',
         auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'),
         name='password_reset'),
    path('reinitialiser-mot-de-passe/envoye/',
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
         name='password_reset_done'),
    path('reinitialiser-mot-de-passe/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reinitialiser-mot-de-passe/complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),
]
