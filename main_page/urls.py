from django.urls import path

from . import views

urlpatterns = [
    path('', views.main_view, name='main'),
    path('results', views.results, name='results'),
]
