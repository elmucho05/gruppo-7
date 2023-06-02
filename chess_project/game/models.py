from django.db import models
from django.contrib.auth.models import User


"""
la stanza esiste solo se ci sono persone dentro, una volta 
che gli utenti sono usciti sarà eliminata
"""
class ChessRoom(models.Model):
  room_name = models.CharField(max_length=6, primary_key=True)
  room_mode = models.IntegerField(default=0)
  def __str__(self):
    return self.room_name

"""
rappresenta i giocatori presenti dentro la stanza durante una partita
"""
class ChessRoomPlayer(models.Model):
  room = models.ForeignKey(ChessRoom, on_delete=models.CASCADE)
  player = models.ForeignKey(User, on_delete=models.CASCADE)
  player_orientation = models.CharField(max_length=5, default='black')
  player_turn = models.BooleanField(default=False)
  player_timer_in_seconds = models.IntegerField(default=5*60)  # default 5 minutes

  class Meta:
    unique_together = (("room", "player"),)
  
  def __str__(self) -> str:
    return f'{self.room}:{self.player}:{self.player_orientation}:{self.player_turn}'
  

"""
rappresenta lo stato di una scacchiera in una partita
"""
class ChessRoomBoard(models.Model):
  room = models.OneToOneField(ChessRoom, on_delete=models.CASCADE)
  fen  = models.CharField(max_length=70, default='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

  def __str__(self):
    return f'{self.room}:{self.fen}'


"""
rappresenta i risultati delle partite effettuate da un utente
"""
class ChessTrackPlayers(models.Model):
  player   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='host')
  opponent = models.ForeignKey(User, null=True, default=None, on_delete=models.CASCADE, related_name='opponent')
  result   = models.CharField(max_length=6, choices=(('winner','winner'), ('loser','loser'), ('draw','draw')))
  score    = models.IntegerField()
  type     = models.CharField(max_length=10, choices=(('public','public'), ('tournament','tournament'),), default='public')

  def __str__(self):
    return f'{self.player}vs{self.opponent} {self.result},{self.score}'


"""
rappresenta un torneo con:
- nome (univoco)
- numero totali di giocatori
- numero corrente di giocatori rimasti
"""
class ChessTournament(models.Model):
  tournament_name     = models.CharField(default='aaaaaa', max_length=6, primary_key=True)

  def __str__(self):
    return f'{self.tournament_name}'


"""
rappresenta una lobby di un torneo con:
- tournament: riferimento a torneo
- player: riferimento al giocatori
"""
class ChessTournamentLobby(models.Model):
  tournament        = models.ForeignKey(ChessTournament, on_delete=models.CASCADE)
  player            = models.ForeignKey(User, on_delete=models.CASCADE)
  num_total_players = models.PositiveIntegerField(default=4) #TODO: da cambiare a 8-16
  turno             = models.PositiveIntegerField(default=0) 

  class Meta:
    unique_together = (("tournament", "player"),)

  def __str__(self) -> str:
    return f'{self.tournament}:{self.player}'
  

