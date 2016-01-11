from Player import Player
from Game import Game
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
        p1=Player(username1,addressPortTuple1)
        p2=Player(username2,addressPortTuple2)
        gameId=str( hash(p1.username+p2.username) )

        self.games[gameId]=Game(p1,p2,gameId,self.sock)

    def play(self, gameId, username, coordinates, customData = None):
        self.games[gameId].play(username,coordinates, customData)

#end Games