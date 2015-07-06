from Player import Player
from Game import Game
import random
import threading

"""
a games object is thread safe
"""
class Games:
	def __init__(self,sock):
		self.games = {}#the key is the gameId, we get the gameId from the player
		self.gamesIsAvailable = True
		self.gamesLock = threading.Lock()
		self.gamesCV = threading.Condition(self.gamesLock)
		self.sock = sock
	#end __init__

	def add(self,username1,username2,addressPortTuple1,addressPortTuple2):
		playerId1=str(hash(username1+str(random.random()) ))
		p1=Player(playerId1,addressPortTuple1,username1)

		playerId2=str(hash(username2+str(random.random()) ))
		p2=Player(playerId2,addressPortTuple2,username2)

		gameId=str(hash(p1.id+p2.id))
		
		game=Game(p1,p2,gameId,self.sock)
		with self.gamesCV:
			while not self.gamesIsAvailable:
				print "Games: add: WAITING for games object"
				self.gamesCV.wait()
				print "Games: add: DONE waiting for games object"

		self.gamesIsAvailable=False
		self.games[game.id]=game
		self.gamesIsAvailable=True

		

	def play(self,gameId,playerId,coordinates):
		with self.gamesCV:
			while not self.gamesIsAvailable:
				print "Games: add: WAITING for games object"
				self.gamesCV.wait()
				print "Games: add: DONE waiting for games object"
		self.gamesIsAvailable=False
		self.games[gameId].play(playerId,coordinates)####DO I REALLY NEED TO USE THE SAME LOCK HERE?(the same lock as the one in the add function)
		self.gamesIsAvailable=True

		
#done with Games
