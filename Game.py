from socket import *
from Player import Player
import json
import threading

class Game:
	"""
	constructor:
	1-assigns self.player1,self.player2,self.id
	2-sends to both players their playerId,gameId,whichPlayer
	"""
	def __init__(self,player1,player2,gameId):
		print "__init__ Game: thread=",threading.current_thread()
		self.player1=player1
		self.player2=player2
		self.id=gameId

		sock=socket(AF_INET,SOCK_DGRAM)
		sock.setsockopt(SOL_SOCKET,SO_REUSEPORT, 1)#so any socket can use this port
		sock.bind(('',5005))

		player1Msg=json.dumps({"playerId":self.player1.id,"gameId":self.id,"whichPlayer":"1"})
		player2Msg=json.dumps({"playerId":self.player2.id,"gameId":self.id,"whichPlayer":"2"})

		print "__init__ Game: sending to players"
		sock.sendto(player1Msg,self.player1.addressPortTuple)
		sock.sendto(player2Msg,self.player2.addressPortTuple)
		print "__init__ Game: done sending to players"
	#done with init

	def play(self,playerId,position):
		tmpSock = socket(AF_INET,SOCK_DGRAM)
		msg=json.dumps({"position":position})
		if playerId==self.player1.id:
			tmpSock.sendto(msg,self.player2.addressPortTuple)
		else:
			tmpSock.sendto(msg,self.player1.addressPortTuple)
	#done with play
#done with Game
