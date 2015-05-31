#one port,one main thread
#if it receives "i wanna play" then it starts a new thread
#to create a game
#this thread runs a function that just keeps waiting until the main thread notifies it to take the other player

from socket import *
import threading,random,json,Queue
from Games import Games

def listeningPlays():#gonna run in a thread
	sock=socket(AF_INET,SOCK_DGRAM)
	sock.bind(('',5006))
	while True:#i will receive playerId,gameId,position from here,
		print "listeningPlays() waiting----------------------"
		msg,addressPortTuple=sock.recvfrom(1024)
		print "listeningPlays() got msg=",msg
		msg=json.loads(msg)
		name=msg["name"]
		playerId=msg["playerId"]
		gameId=msg["gameId"]
		position=msg["position"]
		Games.play(gameId,playerId,position)
	#done with big while
#done with listeningPlays()
##DONE WITH FUNCTIONS

lock=threading.Lock()
cv=threading.Condition(lock)
newPlayersQ=Queue.Queue()#a queue of dicts {username:username,addressPortTuple:addressportTuple}

"""
listenForNewPlayers:
accepts no parameters
creates one "Games" object

while True:
	keep waiting for something to appear on the queue
	take from the queue put it in "pairOfPlayers"
	now see if "pairOfPlayers" has 2 players
	if it has 2 players:
		it takes their usernames,addressPortTuple
		then give it to games.add()
			games.add() generates playerIds and gameId and stuff
			and send the players their ids and stuff
"""
def listenForNewPlayers():
	print "listenForNewPlayers: just started im in thread:",threading.current_thread().getName()
	pairOfPlayers=[]
	games=Games()
	while True:
		with cv:#{
			while newPlayersQ.empty():#{ #just wait while its empty
				print "listenForNewPlayers: waiting for a new player"
				cv.wait()
				print "listenForNewPlayers: done waiting for a new player"
			#}
		#} done with cv
		pairOfPlayers.append(newPlayersQ.get())
		print "listenForNewPlayers: newPlayer=",pairOfPlayers[-1]#-1 means last index

		if len(pairOfPlayers)==2:#{ should pair them together
			print "listenForNewPlayers: count is 2 gonna pair them together"
			username1=pairOfPlayers[0]["username"]
			username2=pairOfPlayers[1]["username"]
			addressPortTuple1=pairOfPlayers[0]["addressPortTuple"]
			addressPortTuple2=pairOfPlayers[1]["addressPortTuple"]
			print "listenForNewPlayers: adding a new game"
			games.add(username1,username2,addressPortTuple1,addressPortTuple2)
			print "listenForNewPlayers: done adding a new game"
			pairOfPlayers=[]
		#} done pairing two players together



#} end listenForNewPlayers()


def main():#{

	sock=socket(AF_INET,SOCK_DGRAM)
	sock.setsockopt(SOL_SOCKET,SO_REUSEPORT, 1)#so any socket can use this port
	sock.bind(('',5005))

	firstPlayerStartingMessage=None
	secondPlayerStartingMessage=None

	listenForNewPlayersThread=threading.Thread(target=listenForNewPlayers)
	listenForNewPlayersThread.name="listenForNewPlayers"
	listenForNewPlayersThread.start()

	while True:#{
		print "main: waiting for message"
		msg,addressPortTuple=sock.recvfrom(1024)
		print "main: got msg=",msg
		msg=json.loads(msg)
		if "username" in msg.keys():#{ wanna play a new game
			with cv:
				print "main: gonna put the player in the queue"
				newPlayersQ.put({"username":msg["username"],"addressPortTuple":addressPortTuple})
				print "main: put him in the queue"
				cv.notify()
				print "main: notified"
		#}
		elif "position" in msg.keys():#{ wanna make a play
			pass
		#}

	#}end while True
#} end main


if __name__ == '__main__':
	main()
