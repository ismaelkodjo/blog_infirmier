from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('a-propos/', views.about, name='about'),
    path('parcours/', views.parcours, name='parcours'),
    path('ressources/', views.resources_page, name='resources_page'),
    path('politique-de-confidentialite/', views.privacy_policy, name='privacy_policy'),
    path('mentions-legales/', views.legal_notice, name='legal_notice'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name='robots'),
]
