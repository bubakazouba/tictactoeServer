"""
maybe i should start a new thread for every addGame and every playGame
i mean inside the method start a new thread, but the problem is that the games object has
to be locked anyways
"""
#### WHAT THE SCRIPT IS DOING:
#one port,one main thread
#if it receives "i wanna play" then it starts a new thread listenForNewTTTPlayers
#to create a game
#this thread runs a function that just keeps waiting until the main thread notifies it to take the other player
#

from Socket import Socket
import threading,random,json,Queue
from Games import Games

sock=Socket(5005)
games=Games(sock)#global games object


newPlaysLock=threading.Lock()
newPlaysCV=threading.Condition(newPlaysLock)
newPlaysQ=Queue.Queue()#a queue of dicts {username:username,addressPortTuple:addressportTuple}
"""
listenForNewPlayers:
accepts no parameters
creates one "Games" object

while True:
    keep waiting for something to appear on the newplaysQ
    take it from the queue and leave it to the games.play() method
"""
def listenForNewPlays():#{
    print "listenForNewPlays||just started im in thread:",threading.current_thread().getName()
    while True:#{
        with newPlaysCV:#{
            while newPlaysQ.empty():# just wait while its empty
                print "listenForNewPlayers||waiting for a new play"
                newPlaysCV.wait()
                print "listenForNewPlayers||done waiting for a new play"
        #done with newPlaysCV
        msg = newPlaysQ.get()#msg is a dict{gameId,username,coordinates}
        gameId = msg["gameId"]
        username = msg["username"]
        coordinates = msg["coordinates"]
        customData = msg.get("customData",None)
        print "listenForNewPlays||SENDING coordinates"
        games.play(gameId,username,coordinates, customData)
        print "listenForNewPlays||DONE sending coordinates"
    #done with while True
#done with listenForNewPlays()


newTTTPlayersLock=threading.Lock()
newTTTPlayersCV=threading.Condition(newTTTPlayersLock)
newTTTPlayersQ=Queue.Queue()#a queue of dicts {username:username,addressPortTuple:addressportTuple}

"""
listenForNewTTTPlayers:
accepts no parameters

while True:
    keep waiting for something to appear on the queue
    take from the queue put it in "pairOfPlayers"
    now see if "pairOfPlayers" has 2 players
    if it has 2 players:
        it takes their usernames,addressPortTuple
        then give it to games.add()
            games.add() generates gameId and stuff
            and send the players their ids and stuff
"""
def listenForNewTTTPlayers():
    print "listenForNewTTTPlayers||just started im in thread:",threading.current_thread().getName()
    pairOfPlayers=[]

    while True:
        with newTTTPlayersCV:
            while newTTTPlayersQ.empty():# just wait while its empty
                print "listenForNewTTTPlayers||WAITING for a new player"
                newTTTPlayersCV.wait()
                print "listenForNewTTTPlayers||DONE waiting for a new player"
            
        # done with newTTTPlayersCV
        pairOfPlayers.append(newTTTPlayersQ.get())
        print "listenForNewTTTPlayers||newPlayer=",pairOfPlayers[-1]#-1 means last index

        if len(pairOfPlayers)==2:# should pair them together
            print "listenForNewTTTPlayers||count is 2 gonna pair them together"
            username1=pairOfPlayers[0]["username"]
            username2=pairOfPlayers[1]["username"]
            addressPortTuple1=pairOfPlayers[0]["addressPortTuple"]
            addressPortTuple2=pairOfPlayers[1]["addressPortTuple"]
            print "listenForNewTTTPlayers||adding a new game"
            games.add(username1,username2,addressPortTuple1,addressPortTuple2)
            print "listenForNewTTTPlayers||done adding a new game"
            pairOfPlayers=[]
        #done pairing two players together

#end listenForNewTTTPlayers()


def main():

    listenForNewTTTPlayersThread = threading.Thread(target=listenForNewTTTPlayers)
    listenForNewTTTPlayersThread.name = "listenForNewTTTPlayers"
    listenForNewTTTPlayersThread.start()

    listenForNewPlaysThread = threading.Thread(target=listenForNewPlays)
    listenForNewPlaysThread.name = "listenForNewPlaysThread"
    listenForNewPlaysThread.start()

    while True:#{
        print "main||WAITING for message<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<",random.randint(1,100)
        msg,addressPortTuple=sock.recvfrom(1024)
        # with open("log.txt","a") as logFile:
            # logFile.write(msg+"\n")
        print "main||GOT msg=",msg
        try:
            msg=json.loads(msg)
        except:
            msg={"msg":msg}
        print "main||got msg="+json.dumps(msg)
        if "coordinates" in msg.keys():#{ wanna make a play
            with newPlaysCV:
                #msg contains the gameId,username,coordinates
                newPlaysQ.put(msg)
                # print "main||DID put him in the newPlaysQ"
                newPlaysCV.notify()
        #end elif "coordinates" in msg.keys()
        elif "username" in msg.keys():# wanna play a new game
            with newTTTPlayersCV:
                msg["addressPortTuple"]=addressPortTuple
                #msg contains the username, addressPortTuple
                print "main||GOING to put him in newTTTPlayersQ"
                newTTTPlayersQ.put(msg)
                # print "main||DID put him in the newTTTPlayersQ"
                newTTTPlayersCV.notify()
        #end wanna play a new game

    #end while True
#end main


if __name__ == '__main__':
    main()
