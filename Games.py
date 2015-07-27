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
        p1=Player(username1,addressPortTuple1)

        p2=Player(username2,addressPortTuple2)

        rand = str(random.random())
        print p1.username, p2.username, rand, type(p1.username)
        gameId=str( hash(p1.username+p2.username+rand) )
        
        game=Game(p1,p2,gameId,self.sock)
        with self.gamesCV:
            while not self.gamesIsAvailable:
                print "Games: add: WAITING for games object"
                self.gamesCV.wait()
                print "Games: add: DONE waiting for games object"

        self.gamesIsAvailable=False
        self.games[game.id]=game
        self.gamesIsAvailable=True

        

    def play(self, gameId, username, coordinates, customData = None):
        with self.gamesCV:
            while not self.gamesIsAvailable:
                print "Games: add: WAITING for games object"
                self.gamesCV.wait()
                print "Games: add: DONE waiting for games object"
        self.gamesIsAvailable=False
        self.games[gameId].play(username,coordinates, customData)####DO I REALLY NEED TO USE THE SAME LOCK HERE?(the same lock as the one in the add function)
        #I don't think I need to use the same lock, (i.e I think I should not use any lock at all) because i'm writing to another place in memory
        self.gamesIsAvailable=True

        
#done with Games
