from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.db.models import Count
from .models import ChessRoom, ChessRoomPlayer, ChessTournament, ChessTournamentLobby, ChessTournamentDraw
from .models import MAX_NUM_PLAYERS_IN_LOBBY
import string, random

def generate_random_room_name():
  return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

"""
view utilizzata per testare le API di chess.js e chessboard.js
"""
def view_test(request):
  return render(request, 'game/test.html')

"""
view che crea una stanza con nome generato casualmente e
reinderizza l'utente in partita
"""
def view_create_room(request):
  # se l'utente non è registrato non può creare partite
  if request.user.is_anonymous:
    messages.error(request, 'Ti devi registrare per iniziare a giocare!')
    return redirect('view_home')
  
  # se l'utente fa già parte di una partita non può crearne una
  if ChessRoomPlayer.objects.filter(player=request.user).exists():
    messages.error(request, 'Fai già parte di una partita!')
    return redirect('view_home')

  room_name = generate_random_room_name()
  ChessRoom.objects.create(room_name=room_name)
  return redirect('view_room', room_name=room_name)


"""
view che crea una stanza con nome generato casualmente e
reinderizza l'utente in partita chess960
"""
def view_create_room960(request):
  # se l'utente non è registrato non può creare partite
  if request.user.is_anonymous:
    messages.error(request, 'Ti devi registrare per iniziare a giocare!')
    return redirect('view_home')
  
  # se l'utente fa già parte di una partita non può crearne una
  if ChessRoomPlayer.objects.filter(player=request.user).exists():
    messages.error(request, 'Fai già parte di una partita!')
    return redirect('view_home')
  
  room_name = generate_random_room_name()
  ChessRoom.objects.create(room_name=room_name,room_mode=1)
  return redirect('view_room', room_name=room_name)


"""
view che cerca delle partite pubbliche disponibili per giocare,
ovvero stanze con un solo giocatore in attesa
"""
def view_search_public_room(request):
  # se l'utente fa già parte di una partita non può crearne una
  if ChessRoomPlayer.objects.filter(player=request.user).exists():
    messages.error(request, 'Fai già parte di una partita!')
    return redirect('view_home')
  
  query = ChessRoomPlayer.objects.values('room').annotate(dcount=Count('room')).order_by()
  for item in query:
    room   = item['room']
    dcount = item['dcount']
    if dcount == 1:
      return redirect('view_room', room)

  messages.error(request, 'Non ci sono partite disponibili')
  return redirect('view_home')
  

def view_home(request):
  action = request.GET.get('action', None)
  room_name = request.GET.get('room', None)
  if action == 'join':
    return redirect('view_room', room_name)
  if action == 'spect':
    return redirect('view_spectator', room_name)
  
  context = {}
  if not request.user.is_anonymous:
    player_room = ChessRoomPlayer.objects.filter(player=request.user)
    if player_room.exists():
      context['player_room'] = player_room.first()

  return render(request, 'game/home.html', context)

def view_singleplayer(request):
  return render(request, 'game/singleplayer.html')

def view_spectator(request, room_name):
  # controllo se la stanza esiste
  room = ChessRoom.objects.filter(room_name=room_name)
  if not room.exists():
    messages.error(request, mark_safe(f'La stanza <b>{room_name}</b> non esiste o è stata eliminata'))
    return redirect('view_home') 
  
  return render(request, 'game/spectator.html', {'room_name' : room_name})

def view_room(request, room_name):
  # se l'utente non è registrato non può giocare
  if request.user.is_anonymous:
    messages.error(request, 'Ti devi registrare per iniziare a giocare!')
    return redirect('view_home')
  
  # se l'utente fa già parte di una partita e prova ad entrare in una partita diversa
  player_room = ChessRoomPlayer.objects.filter(player=request.user)
  if player_room.exists(): 
    player_room = player_room.first()
    if player_room.room.room_name != room_name:
      messages.error(request, 'Fai già parte di una partita!')
      return redirect('view_home')
  
  # controllo se la stanza esiste
  room = ChessRoom.objects.filter(room_name=room_name)
  if not room.exists():
    messages.error(request, mark_safe(f'La stanza <b>{room_name}</b> non esiste o è stata eliminata'))
    return redirect('view_home')
  
  room = room.first()
  room_player = ChessRoomPlayer.objects.filter(room=room, player=request.user)
  num_players = ChessRoomPlayer.objects.filter(room=room).count()

  # se l'utente non fa già parte della partita e prova a entrare in una stanza piena 
  if not room_player.exists() and num_players == 2:
    messages.error(request, f'La stanza è già piena')
    return redirect('view_home')

  room_page = "game/room.html"
  if room.room_mode == 1:
    room_page = "game/room960.html"
  
  return render(request, room_page, {'room_name': room_name})

def view_tornament_lobby(request, tournament_name):
  # se l'utente non è registrato non può giocare
  if request.user.is_anonymous:
    messages.error(request, 'Ti devi registrare per iniziare a giocare!')
    return redirect('view_home')
  
  # se l'utente fa già parte di una partita non può entrare in un torneo
  if ChessRoomPlayer.objects.filter(player=request.user).exists():
    messages.error(request, 'Non puoi partecipare ad un torneo mentre sei in partita!')
    return redirect('view_home')
  
  tournament = ChessTournament.objects.get(tournament_name=tournament_name)

  player_lobby = ChessTournamentLobby.objects.filter(tournament=tournament, player=request.user)
  num_players = ChessTournamentLobby.objects.filter(tournament=tournament).count()

  # se l'utente prova ad entrare in una lobby piena
  if not player_lobby.exists() and num_players == MAX_NUM_PLAYERS_IN_LOBBY:
    messages.error(request, 'La lobby per il torneo è piena')
    return redirect('view_home')
  
  return render(request, 'game/tournament-lobby.html', {'tournament_name' : tournament_name})
