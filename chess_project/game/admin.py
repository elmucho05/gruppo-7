from django.contrib import admin
from .models import ChessRoom, ChessRoomPlayer, ChessRoomBoard, ChessTrackPlayers
from .models import ChessTournament, ChessTournamentLobby

# Register your models here.
admin.site.register(ChessRoom)
admin.site.register(ChessRoomPlayer)
admin.site.register(ChessRoomBoard)
admin.site.register(ChessTrackPlayers)
admin.site.register(ChessTournament)
admin.site.register(ChessTournamentLobby)