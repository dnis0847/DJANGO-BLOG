from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('blog/', views.blog, name='blog'),
    path('contacts/', views.contacts, name='contacts'),
    path('about/', views.about, name='about'),
    path('blog/post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('blog/category/<slug:slug>/', views.category_list, name='category_list'),
    path('blog/tag/<slug:slug>/', views.tag_list, name='tag_list'),
    path('search/', views.search, name='search'),
    path('blog/success/', views.contact_success, name='contact_success'),
    path('subscribe/', views.subscribe, name='subscribe'),
]
