import Socket
from Player import Player
import json
import threading

class Game:
    """
    constructor:
    1-assigns self.player1,self.player2,self.id
    2-creates a socket (self.sock)
    3-sends to both players their gameId,whichPlayer
    """
    def __init__(self,player1,player2,gameId,sock):
        self.player1=player1
        self.player2=player2
        self.id=gameId

        self.sock=sock

        player1Msg={"gameId":self.id,"whichPlayer":"1"}
        player2Msg={"gameId":self.id,"whichPlayer":"2"}
        print "pair: "+player1.username+" "+player2.username
        self.sock.sendto(player1Msg,self.player1.addressPortTuple)
        self.sock.sendto(player2Msg,self.player2.addressPortTuple)
    #end __init__

    """
    play(username,coordinates):
    1-takes username and coordinates
    2-checks if this is player1 then send to player2 and vice versa
    """
    def play(self,username,coordinates, customData = None):
        
        msg={"coordinates":coordinates, "gameId": self.id}
        if customData is not None:
            msg["customData"] = customData
            
        if username==self.player1.username:
            self.sock.sendto(msg,self.player2.addressPortTuple)
        else:
            self.sock.sendto(msg,self.player1.addressPortTuple)
    #end play
#end Game
