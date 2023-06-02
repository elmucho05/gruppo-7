from django.urls import path

from . import views

urlpatterns = [
  # http://127.0.0.1:8000/test
  path("test", views.view_test, name="view_test"),

  # http://127.0.0.1:8000/home
  path("home", views.view_home, name="view_home"),
  path('', views.view_home, name='view_home'),
  # http://127.0.0.1:8000/singleplayer
  path('singleplayer', views.view_singleplayer, name="view_singleplayer"),

  # http://127.0.0.1:8000/create-room
  path("create-room", views.view_create_room, name="view_create_room"),

  # http://127.0.0.1:8000/search-available-room
  path("search-public-room", views.view_search_public_room, name="view_search_public_room"),

  # http://127.0.0.1:8000/room/<name>
  path('room/<str:room_name>', views.view_room, name="view_room"),


  # http://127.0.0.1:8000/tournament/<name>
  path('tournament-lobby/<str:tournament_name>', views.view_tornament_lobby, name="view_tornament_lobby"),

  # path per room degli scacchi960
  # http://127.0.0.1:8000/create-room960
  path("create-room960", views.view_create_room960, name="view_create_room960"),

  # http://127.0.0.1:8000/spectator/room/<name>
  path('spectator/room/<str:room_name>', views.view_spectator, name="view_spectator"),
]