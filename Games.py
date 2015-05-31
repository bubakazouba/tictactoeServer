from Player import Player
from Game import Game
import random

class Games:
	def __init__(self):
		self.arr={}#the key is the gameId, we get the gameId from the player

	def add(self,username1,username2,addressPortTuple1,addressPortTuple2):
		playerId1=hash(username1+str(random.random()) )
		p1=Player(playerId1,addressPortTuple1,username1)

		playerId2=hash(username2+str(random.random()) )
		p2=Player(playerId2,addressPortTuple2,username2)

		gameId=hash(p1.id+p2.id)
		
		game=Game(p1,p2,gameId)
		self.arr[game.id]=game

	def play(self,gameId,playerId,position):
		self.arr[gameId].play(playerId,position)
#done with Games
