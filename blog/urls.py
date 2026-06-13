from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('recherche/', views.search_view, name='search'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<slug:slug>/', views.category_detail, name='category_detail'),
    path('nouvel-article/', views.article_create, name='article_create'),
    path('<slug:slug>/', views.article_detail, name='article_detail'),
    path('<slug:slug>/modifier/', views.article_edit, name='article_edit'),
    path('<slug:slug>/supprimer/', views.article_delete, name='article_delete'),
    path('commentaire/<int:comment_id>/signaler/', views.flag_comment, name='flag_comment'),
]
