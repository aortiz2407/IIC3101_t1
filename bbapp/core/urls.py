from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('', views.episode_view, name="episode"),
    path('', views.character_view, name="character")
]
