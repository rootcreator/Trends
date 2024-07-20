from django.urls import path
from . import views
from .views import set_region

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_trends, name='search_trends'),
    path('update/', views.update_trends, name='update_trends'),
    path('set_region/', set_region, name='set_region'),
]
