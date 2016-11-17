#### WHAT THE SCRIPT IS DOING:
# one port,one main thread
# if it receives "i wanna play" then it starts a new thread listenForNewTTTPlayers
# to create a game
# this thread runs a function that just keeps waiting until the main thread notifies it to take the other player

from Socket import Socket
import threading,random,json,Queue
from Games import Games

sock=Socket(5005)
games=Games(sock)#global games object


newPlaysLock=threading.Lock()
newPlaysCV=threading.Condition(newPlaysLock)
newPlaysQ=Queue.Queue()#a queue of dicts {username:username,addressPortTuple:addressportTuple}

def listenForNewPlays():#{
    """
    listenForNewPlayers:
    accepts no parameters
    creates one "Games" object

    while True:
        keep waiting for something to appear on the newplaysQ
        take it from the queue and leave it to the games.play() method
    """
    while True:#{
        with newPlaysCV:#{
            while newPlaysQ.empty():# just wait while its empty
                newPlaysCV.wait()

        msg = newPlaysQ.get()#msg is a dict{gameId,username,coordinates}
        gameId = msg["gameId"]
        username = msg["username"]
        coordinates = msg["coordinates"]
        customData = msg.get("customData",None)
        games.play(gameId,username,coordinates, customData)
    #done with while True
#done with listenForNewPlays()


newTTTPlayersLock=threading.Lock()
newTTTPlayersCV=threading.Condition(newTTTPlayersLock)
newTTTPlayersQ=Queue.Queue()#a queue of dicts {username:username,addressPortTuple:addressportTuple}


def listenForNewTTTPlayers():
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
    print "listenForNewTTTPlayers||just started im in thread:",threading.current_thread().getName()
    pairOfPlayers=[]

    while True:
        with newTTTPlayersCV:
            while newTTTPlayersQ.empty():# just wait while its empty
                newTTTPlayersCV.wait()
            
        pairOfPlayers.append(newTTTPlayersQ.get())
        print "listenForNewTTTPlayers||newPlayer=",pairOfPlayers[-1]#-1 means last index

        if len(pairOfPlayers)==2:# should pair them together
            print "listenForNewTTTPlayers||count is 2 gonna pair them together"
            username1=pairOfPlayers[0]["username"]
            username2=pairOfPlayers[1]["username"]
            addressPortTuple1=pairOfPlayers[0]["addressPortTuple"]
            addressPortTuple2=pairOfPlayers[1]["addressPortTuple"]
            games.add(username1,username2,addressPortTuple1,addressPortTuple2)
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

    while True:
        print "main||WAITING for message<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<",random.randint(1,100)
        msg,addressPortTuple=sock.recvfrom(1024)
        try:
            msg=json.loads(msg)
        except:
            msg={"msg":msg}
        print "main||got msg="+json.dumps(msg)
        if "coordinates" in msg.keys(): # want to make a play
            with newPlaysCV:
                #msg contains the gameId,username,coordinates
                newPlaysQ.put(msg)
                newPlaysCV.notify()
        #end elif "coordinates" in msg.keys()
        elif "username" in msg.keys():# wanna play a new game
            with newTTTPlayersCV:
                msg["addressPortTuple"]=addressPortTuple
                #msg contains the username, addressPortTuple
                newTTTPlayersQ.put(msg)
                newTTTPlayersCV.notify()
        #end wanna play a new game

    #end while True
#end main


if __name__ == '__main__':
    main()
