from django.urls import path
from . import views
app_name = 'newsletter'
urlpatterns = [
    path('inscription/', views.subscribe_view, name='subscribe'),
    path('desinscription/<uuid:token>/', views.unsubscribe_view, name='unsubscribe'),
]
