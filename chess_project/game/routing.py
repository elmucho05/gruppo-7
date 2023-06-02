# chat/routing.py
from django.urls import path

from . import consumer

websocket_urlpatterns = [
  path('ws/room/<str:room_name>', consumer.PlayerConsumer.as_asgi()),
  path('ws/spectator/room/<str:room_name>', consumer.SpectatorConsumer.as_asgi()),

  path('ws/tournament-lobby/<str:tournament_name>', consumer.TournamentLobbyConsumer.as_asgi()),
]