from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import ChessTournament, ChessTournamentLobby, ChessRoom, ChessTournamentDraw
from .models import MAX_NUM_PLAYERS_IN_LOBBY
from .views import generate_random_room_name
import json


"""
utilizzata nella lobby del torneo
"""
class TournamentStatus:
  WAITING_FOR_PLAYER = "WAITING_FOR_PLAYER"
  READY_TO_DRAW      = "READY_TO_DRAW"
  PLAYERS_IN_GAME    = "PLAYERS_IN_GAME"
  TOURNAMENT_CLOSED  = "TOURNAMENT_CLOSED"

class TournamentLobbyStatus:
  WAITING = 'WAITING'
  IN_GAME = 'IN_GAME'


"""
Lobby torneo
"""
class TournamentLobbyConsumer(WebsocketConsumer):
  
  # ws://127.0.0.1/ws/tournament-lobby/<str:tournament_name>
  def connect(self):
    self.tournament_name = self.scope["url_route"]["kwargs"]["tournament_name"]
    
    self.user = self.scope['user']
    
    async_to_sync(self.channel_layer.group_add)(self.tournament_name, self.channel_name)
    
    self.accept()

    self.tournament = ChessTournament.objects.get(tournament_name=self.tournament_name)

    lobby_player = ChessTournamentLobby.objects.filter(tournament=self.tournament, player=self.user)
    
    # if player is reconnecting to lobby or tournament is close:
    # only send info about lobby and tournament
    if lobby_player.exists() or self.is_tournament_closed():
      self.send_lobby_info(echo_group=False)
      
    
    # if lobby is not full insert new player
    elif self.is_tournament_waiting() and not lobby_player.exists():
      self.push_player_in_lobby()
      self.send_lobby_info(echo_group=True)

    
    # if tournament is ready to draw
    if self.is_tournament_ready_to_draw():
      # get only qualified player to draw
      qual_players = ChessTournamentLobby.objects.filter(player_is_qualified=True)
      
      # create (qual_players/2) rooms
      # num_rooms    = int(len(qual_players) / 2) 
      # room_names = [generate_random_room_name() for i in range(num_rooms)]
      # ChessRoom.objects.bulk_create([ChessRoom(name) for name in room_names])
      
      # delete previously draw if exists
      ChessTournamentDraw.objects.filter(tournament=self.tournament).delete()
      
      # insert new draw
      # draws = self.generate_draws(qual_players)
      # ChessTournamentDraw.objects.bulk_create([
      #   ChessTournamentDraw(tournament=self.tournament, player1=draw[0], player2=draw[1]) for draw in draws 
      # ])
      
      self.send_lobby_info(echo_group=True)




  """ On receive """
  def receive(self, text_data:str = None, bytes_data=None):
    data_json = json.loads(text_data)
    
    if 'quit-lobby' in data_json:
      self.on_quit_lobby()
  
  """ On disconnect """
  def disconnect(self, code): 
    async_to_sync(self.channel_layer.group_discard)(self.tournament_name, self.channel_name)
    self.close()
 
  def echo(self, event):
    self.send(text_data=json.dumps(event['context']))

  def echo_group(self, context):
    async_to_sync(self.channel_layer.group_send)(self.tournament_name, {
      "type": "echo",
      "context": context
    })

  """ Send to group info about lobby """
  def send_lobby_info(self, echo_group):
    players, num_players = self.get_players_in_lobby()
    tournament_draws = ChessTournamentDraw.objects.filter(tournament=self.tournament) 
    draws = [ (d.player1.username, d.player2.username) for d in tournament_draws ]
    winner = "#USER"
    if echo_group:
      self.echo_group({
        'tournament-status' : self.tournament.tournament_status,
        'tournament-round'  : self.tournament.tournament_round,
        'lobby' : {
          'total-num-players'   : MAX_NUM_PLAYERS_IN_LOBBY,
          'current-num-players' : num_players,
          'players'             : players,
        },
        'draws'  : draws,      
        'winner' : winner,
      })
    else:
      self.send(text_data=json.dumps({
        'tournament-status' : self.tournament.tournament_status,
        'tournament-round'  : self.tournament.tournament_round,
        'lobby' : {
          'total-num-players'   : MAX_NUM_PLAYERS_IN_LOBBY,
          'current-num-players' : num_players,
          'players'             : players
        },
        'draws'  : draws,
        'winner' : winner,
      }))

    

  """ Returns player list who are in tournament lobby and the len the list """
  def get_players_in_lobby(self):
    tournament_lobby = ChessTournamentLobby.objects.filter(tournament=self.tournament) 
    # players = [ ( user, qualified, status ), (...), (...) ]
    players = [ (p.player.username, p.player_is_qualified, p.player_status) for p in tournament_lobby ]
    num_players = len(players)
    return (players, num_players)
  
  """ Insert player in tournament lobby and update tournament status if lobby is full """
  def push_player_in_lobby(self):
    ChessTournamentLobby.objects.create(tournament=self.tournament, player=self.user)
    _, num_players = self.get_players_in_lobby()
    if self.is_lobby_full(num_players):
      self.tournament.tournament_status = 'READY_TO_DRAW'
      self.tournament.save()



  """ Returns True if tournament status is TOURNAMENT_CLOSED """
  def is_tournament_closed(self):
    return self.tournament.tournament_status == TournamentStatus.TOURNAMENT_CLOSED

  """ Returns True if tournament status is WAITING_FOR_PLAYERS """
  def is_tournament_waiting(self):
    return self.tournament.tournament_status == TournamentStatus.WAITING_FOR_PLAYER

  """ Returns True if tournament status is READY_TO_DRAW """
  def is_tournament_ready_to_draw(self):
    return self.tournament.tournament_status == TournamentStatus.READY_TO_DRAW

  """ Returns True if lobby is full (num_players=MAX_NUM_PLAYERS_IN_LOBBY)"""
  def is_lobby_full(self, num_players):
    return num_players == MAX_NUM_PLAYERS_IN_LOBBY



  """ Generate randomly draws """
  def generate_draws(self, qual_players):
    player_list  = [ p.player.username for p in qual_players ] 
    # draws = [ (user,user), (user,user), (...) ]
    draws = [ (player_list[i:i+1]) for i in range(0, len(player_list), 2)]
    return draws
  


  """ Called when player quit tournament lobby """
  def on_quit_lobby(self):
    # remove player from lobby
    ChessTournamentLobby.objects.get(tournament=self.tournament, player=self.user).delete()
    
    # update tournament status
    tournament = ChessTournament.objects.get(tournament_name=self.tournament_name)
    tournament.tournament_status = TournamentStatus.WAITING_FOR_PLAYER
    tournament.save()

    # send to group info about lobby
    self.send_lobby_info(echo_group=True)


