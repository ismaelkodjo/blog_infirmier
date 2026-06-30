from django.urls import path
from . import views

app_name = 'formations'

urlpatterns = [
    path('',                                      views.formations_home,          name='home'),
    path('<slug:slug>/',                           views.formation_detail,         name='detail'),
    path('<slug:slug>/inscription/',               views.inscription,              name='inscription'),
    path('confirmation/<str:numero>/',             views.inscription_confirmation,  name='inscription_confirmation'),
    path('mon-espace/',                            views.espace_apprenant,         name='espace_apprenant'),
    path('<slug:slug>/lecon/<int:lecon_id>/',      views.lecon_detail,             name='lecon'),
]
