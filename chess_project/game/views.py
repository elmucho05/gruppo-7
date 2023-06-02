from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.db.models import Count
from .models import ChessRoom, ChessRoomPlayer, ChessTournament, ChessTournamentLobby
import string, random

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
  
  room_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
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
  room_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
  ChessRoom.objects.create(room_name=room_name,room_mode=1)
  return redirect('view_room', room_name=room_name)


"""
view che cerca delle partite pubbliche disponibili per giocare,
ovvero stanze con un solo giocatore in attesa
"""
def view_search_public_room(request):
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

  return render(request, 'game/home.html')

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
  
  # controllo se la stanza esiste
  room = ChessRoom.objects.filter(room_name=room_name)
  if not room.exists():
    messages.error(request, mark_safe(f'La stanza <b>{room_name}</b> non esiste o è stata eliminata'))
    return redirect('view_home')
  
  room = room.first()
  if room.room_mode == 0:
    return render(request, 'game/room.html', {'room_name': room_name})
  else:
    return render(request, 'game/room960.html', {'room_name': room_name})

  # controllo se il giocatore sia già in partita (nel caso di ricaricamento della pagina)
  room_player = ChessRoomPlayer.objects.filter(room=room, player=request.user)
  if room_player.exists():
    return render(request, 'game/room.html', {'room_name' : room_name})

  # controllo se la stanza è piena 
  num_players = ChessRoomPlayer.objects.filter(room=room).count()
  if num_players == 2:
    messages.error(request, f'La stanza è già piena')
    return redirect('view_home')
  
  return render(request, 'game/room.html', {'room_name' : room_name})

def view_tornament_lobby(request, tournament_name):
  # se l'utente non è registrato non può giocare
  if request.user.is_anonymous:
    messages.error(request, 'Ti devi registrare per iniziare a giocare!')
    return redirect('view_home')
  
  tournament = ChessTournament.objects.get(tournament_name=tournament_name)
  
  # se l'utente fa già parte della lobby
  if ChessTournamentLobby.objects.filter(tournament=tournament, player=request.user).exists():
    return render(request, 'game/tournament-lobby.html', {'tournament_name' : tournament_name})
  
  # se la lobby è piena l'utente non può entrare
  num_players = ChessTournamentLobby.objects.filter(tournament=tournament).count()
  if num_players == tournament.num_total_players:
    messages.error(request, 'La lobby per il torneo è piena')
    return redirect('view_home')



  return render(request, 'game/tournament-lobby.html', {'tournament_name' : tournament_name})
