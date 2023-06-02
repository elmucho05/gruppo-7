from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import ChessRoom, ChessRoomPlayer, ChessRoomBoard, ChessTrackPlayers
import json, random

# user 1: 
#   username: Liam
#   email:    liam@gmail.com
#   passwd:   atelegib
# user 2: 
#   username: Noah
#   email:    noah@gmail.com
#   passwd:   oundrecu
# user 3: 
#   username: Oliver
#   email:    oliver@gmail.com
#   passwd:   ilockalo
# user 4: 
#   username: Kane
#   email:    kane@gmail.com
#   passwd:   tANdbusT


"""
utilizzata durante una partita
"""
class GameStatus:
  WAITING_FOR_PLAYER = "WAITING_FOR_PLAYER" # 1 only player in room
  GAME_READY         = "GAME_READY"         # 2 players in room
  GAME_END           = "GAME_END"           # end game


"""
Modalità spettatore
"""
class SpectatorConsumer(WebsocketConsumer):
  
  # ws://127.0.0.1/ws/spectator/room/<str:room_name>
  def connect(self):
    self.room_name = self.scope["url_route"]["kwargs"]["room_name"]

    async_to_sync(self.channel_layer.group_add)(self.room_name, self.channel_name)

    self.accept()

    self.room = ChessRoom.objects.get(room_name=self.room_name)
    num_players = ChessRoomPlayer.objects.filter(room=self.room).count()
    if num_players == 2:
      board = ChessRoomBoard.objects.get(room=self.room)
      players = list(ChessRoomPlayer.objects.filter(room=self.room)) 

      self.send(text_data=json.dumps({
        'start-game' : {
          'player-orientation' : {
            players[0].player.username : players[0].player_orientation,
            players[1].player.username : players[1].player_orientation,
          },
          'player-turn' : {
            players[0].player.username : players[0].player_turn,
            players[1].player.username : players[1].player_turn,
          },
          'fen' : board.fen
        },
      }))

  
  def receive(self, text_data:str = None, bytes_data=None):
    data_json = json.loads(text_data)
    print(data_json)
  
  def disconnect(self, code):   
    async_to_sync(self.channel_layer.group_discard)(self.room_name, self.channel_name)

    self.close()
 
  def echo(self, event):
    self.send(text_data=json.dumps(event['context']))

  def echo_group(self, context):
    async_to_sync(self.channel_layer.group_send)(self.room_name, {
      "type": "echo",
      "context": context
    })


"""
Stanza 1v1
"""
class PlayerConsumer(WebsocketConsumer):

  # ws://127.0.0.1/ws/room/<str:room_name>
  def connect(self):
    self.room_name = self.scope["url_route"]["kwargs"]["room_name"]

    async_to_sync(self.channel_layer.group_add)(self.room_name, self.channel_name)

    self.accept()

    self.user = self.scope['user']

    self.room = ChessRoom.objects.get(room_name=self.room_name)
    
    # new connection
    room_player, created = ChessRoomPlayer.objects.get_or_create(room=self.room, player=self.user)
    if created:
      # first player connected event:
      # - send WAITING_FOR_PLAYER signal
      if self.num_players_in_room() == 1: 
        self.send_waiting_signal()
      
      # the second player connected event:
      # - create board
      # - init player roles
      # - start game
      elif self.num_players_in_room() == 2:
        board, _ = ChessRoomBoard.objects.get_or_create(room=self.room)
        players = self.init_player_roles()
        self.start_game(players, board)

    # on reload page 
    else:
      self.on_reload_page()


  """ On receive message event """
  def receive(self, text_data:str = None, bytes_data=None):
    data_json = json.loads(text_data)

    # [in-game event] on move pawn event 
    if 'new-fen' in data_json:
      new_fen = data_json['new-fen'] 
      move = data_json['move']
      self.on_move_pawn(new_fen, move)
    
    # [in-game event] update timer every second
    if 'decrement-player-timer' in data_json:
      self.on_decrement_timer()

    # [end-game event] on player left game
    if 'quit-game-player' in data_json:
      self.on_quit_game()
    
    # [end-game event] on player quit room
    if 'quit-room' in data_json:
      self.on_quit_room()

    # [end-game event] on checkmate
    if 'checkmate' in data_json:
      self.on_checkmate()

    # echo messages between players
    self.echo_group(data_json)

  """ On disconnect event """
  def disconnect(self, code):    
    async_to_sync(self.channel_layer.group_discard)(self.room_name, self.channel_name)
    self.close()

  """ Send message callback """
  def echo(self, event):
    self.send(text_data=json.dumps(event['context']))

  """ Echo message to group users """
  def echo_group(self, context):
    async_to_sync(self.channel_layer.group_send)(self.room_name, {
      "type": "echo",
      "context": context
    })

  """ Player reconnect on same room """
  def on_reload_page(self):
    if self.num_players_in_room() == 1:
      self.send_waiting_signal()

    elif self.num_players_in_room() == 2:
      board = ChessRoomBoard.objects.get(room=self.room)
      players = list(ChessRoomPlayer.objects.filter(room=self.room)) 
      self.start_game(players, board)

  """ Send WAITING_FOR_PLAYERS signal """
  def send_waiting_signal(self):
    self.send(text_data=json.dumps({'game-status-code': GameStatus.WAITING_FOR_PLAYER}))

  """ Get number of players in room """
  def num_players_in_room(self):
    return ChessRoomPlayer.objects.filter(room=self.room).count()
  
  """ Start Chess game """
  def start_game(self, players, board):
    # echo group player orientations and fen
    self.echo_group({
      'game-status-code': GameStatus.GAME_READY,
      'start-game' : {
        'player-orientation' : {
          players[0].player.username : players[0].player_orientation,
          players[1].player.username : players[1].player_orientation,
        },
        'player-turn' : {
          players[0].player.username : players[0].player_turn,
          players[1].player.username : players[1].player_turn,
        },
        'player-timer' :{
          players[0].player.username : players[0].player_timer_in_seconds,
          players[1].player.username : players[1].player_timer_in_seconds,
        },
        'fen' : board.fen
      },
    })

  """ It's randomly decided who starts black or white """
  def init_player_roles(self):
    random_index = random.randint(0, 1)
    players = list(ChessRoomPlayer.objects.filter(room=self.room))
    for index, p in enumerate(players):
      if index == random_index:
        p.player_orientation = 'white'
        p.player_turn = True
        p.save()
      else:
        p.player_orientation = 'black'
        p.player_turn = False
        p.save()
    return players

  """ Called when player move a pawn """
  def on_move_pawn(self, new_fen, move):
    # swap player turns
    players = list(ChessRoomPlayer.objects.filter(room=self.room)) 
    for player in players:
      player.player_turn = not player.player_turn
      player.save()

    # update chess board fen 
    board = ChessRoomBoard.objects.get(room=self.room)
    board.fen = new_fen 
    board.save()

    # echo new turns and new fen
    self.echo_group({
      'in-game' : {
        'swap-turn' : {
          players[0].player.username : players[0].player_turn,
          players[1].player.username : players[1].player_turn,
        },
        'new-fen' : board.fen,
        'move' : move
      }
    })

  """ Called when player quit room without penalty """
  def on_quit_room(self):
    # delete player from ChessRoomPlayer table
    ChessRoomPlayer.objects.get(room=self.room, player=self.user).delete()

    # delete room if empty 
    if self.num_players_in_room() == 0:
      self.room.delete()

  """ Called when player quit game with penalty (during the game) """
  def on_quit_game(self):
    loser  = self.user
    winner = ChessRoomPlayer.objects.filter(room=self.room).exclude(player=loser).first().player
    ChessTrackPlayers.objects.create(player=loser, opponent=winner, result='loser', score=-1)
    ChessTrackPlayers.objects.create(player=winner, opponent=loser, result='winner', score=1)
    
    self.on_quit_room()

    # echo player left game
    self.echo_group({
      'game-status-code': GameStatus.GAME_END,
      'end-game' : { 
        'reason' : 'player-left',
        'player' : loser.username
      },
    })

  """ Called when player time out """
  def on_timeout(self):
    loser  = self.user
    winner = ChessRoomPlayer.objects.filter(room=self.room).exclude(player=loser).first().player
    ChessTrackPlayers.objects.create(player=loser, opponent=winner, result='loser', score=-1)
    ChessTrackPlayers.objects.create(player=winner, opponent=loser, result='winner', score=1)
    
    self.echo_group({
      'game-status-code': GameStatus.GAME_END,
      'end-game' : {
        'reason' : 'player-timeout',
        'player' : loser.username
      }
    })
  
  """ Called every second """
  def on_decrement_timer(self):
    room_player = ChessRoomPlayer.objects.get(room=self.room, player=self.user)
    room_player.player_timer_in_seconds -= 1
    room_player.save()

    if room_player.player_timer_in_seconds < 0:
      self.on_timeout()

  """ Called on checkmate """
  def on_checkmate(self):
    winner = self.user
    loser  = ChessRoomPlayer.objects.filter(room=self.room).exclude(player=winner).first().player
    ChessTrackPlayers.objects.create(player=loser, opponent=winner, result='loser', score=-1)
    ChessTrackPlayers.objects.create(player=winner, opponent=loser, result='winner', score=1)
    
    self.echo_group({
      'game-status-code': GameStatus.GAME_END,
      'end-game' : {
        'reason' : 'checkmate',
        'winner' : winner.username
      }
    })
  
