# chat/routing.py
from django.urls import path

from . import room_consumer, tournament_consumer

websocket_urlpatterns = [
  path('ws/room/<str:room_name>', room_consumer.PlayerConsumer.as_asgi()),
  path('ws/spectator/room/<str:room_name>', room_consumer.SpectatorConsumer.as_asgi()),

  path('ws/tournament-lobby/<str:tournament_name>', tournament_consumer.TournamentLobbyConsumer.as_asgi()),
]