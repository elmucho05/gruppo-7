import unittest

class TestGame(unittest.TestCase):
  def setUp(self):
    self.players = ['admin', 'liam', 'oliver', 'noah']
    
  def test_tournament_draws(self):
    match_list = [ tuple(self.players[i:i+2])  for i in range(0, len(self.players), 2)]
    self.assertEqual([ ('admin', 'liam'), ('oliver', 'noah') ] , match_list)



