from django.urls import path
from . import views

app_name = 'boutique'

urlpatterns = [
    path('',                            views.boutique_home,         name='home'),
    path('produit/<slug:slug>/',        views.produit_detail,        name='produit'),
    path('panier/',                     views.panier_detail,         name='panier'),
    path('panier/ajouter/<int:produit_id>/', views.panier_ajouter,  name='panier_ajouter'),
    path('panier/modifier/<int:ligne_id>/',  views.panier_modifier,  name='panier_modifier'),
    path('panier/supprimer/<int:ligne_id>/', views.panier_supprimer, name='panier_supprimer'),
    path('commander/',                  views.commander,             name='commander'),
    path('confirmation/<str:numero>/',  views.commande_confirmation,  name='commande_confirmation'),
]
