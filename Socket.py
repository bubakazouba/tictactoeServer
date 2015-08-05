"""
TODO:
instead of one thread for every send
make it just one thread that handles all of these
so the send function just sends and adds it to the dict: (msg,addressPortTuple,timesent)
(if i got an ack in the __listen function i remove from the dict)
the thread loops in the dict and sees if anything needs sending again, it sends if it needs sending
"""

import sys
import socket
import threading
import Queue #synchronized queue
import json
import time #for sleeping 
from ACKManager import ACKManager
from Dict import Dict
from Packet import Packet

class Socket:
    def __init__(self,port=None):
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        # self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT, 1)#so any socket can use this port
        if port is not None:
            self.sock.bind(('',port))

        #stuff for receiving
        #when received something, put it in the recvMsgsQ
        #so it can be procesed
        self.recvMsgsLock = threading.Lock()
        self.recvMsgsCV = threading.Condition(self.recvMsgsLock)
        self.recvMsgsQ = Queue.Queue()#a queue of messages available to be returned through recv function


        #array of packets that are sent and server is waiting for their ACKs
        self.pendingACKsPacketsLock = threading.Lock()
        self.pendingACKsPackets = []


        self.recvACKs  = Dict() #ACKs[addressPortTuple] = [list of ACKs of messages that are received and proccessed]
        #so when server gets a message it knows wether it was received before so it can safely ignore it

        self.ACKManager = ACKManager() #manages acks for messages sent

        self.__startUpWaitingForAcksThread()
        self.__startUpListeningThread()
    #end init    

    def sendto(self,msg,addressPortTuple):
        sendThread = threading.Thread(target = self.__sendto,args = (msg,addressPortTuple))
        sendThread.name = "sendto"+json.dumps(addressPortTuple)
        sendThread.start()

    def __sendto(self,msg,addressPortTuple):
        """
        args:
        msg: dict
        addressPortTuple: tuple
        
        get the maximum ack number of the list of acks, add 1 to it
        set that to be the ack of the message being sent
        put in the list of acks that number

        return: None
        """
        msg["ack"] = str( self.ACKManager.getACK(addressPortTuple) )

        self.sock.sendto(json.dumps(msg),addressPortTuple)
        # print "Socket||__sendto||"+json.dumps(addressPortTuple),"ack=",msg["ack"]
        print "added ",msg["ack"], "to pending"
        self.pendingACKsPackets.append( Packet( msg, int(msg["ack"]), addressPortTuple, time.time() ) )
        time.sleep(0.5)
    #end sendto

    def __startUpWaitingForAcksThread(self):
        waitingForAcks = threading.Thread(target = self.__waitingForAcks)
        waitingForAcks.name = "waiting for acks thread"
        waitingForAcks.start()

    def __waitingForAcks(self):
        """
        a function to be ran in a thread
        this function is meant to keep looping an array of Packets
        if 0.5 seconds have passed on any msg it resends it and resets the lastTimeSent
        it uses the ack of the message to check in ACKManager if it was confirmed (we know it was confirmed through the __listen)

        arrayToBeLooped is the array gonna be looped on everytime
        self.pendingACKsPackets is the global array whenever server sends something it appends it to this array 
        """
        arrayToBeLooped = []
        packetsNotConfirmed = []
        while True:
            #add anything pending from outside
            self.pendingACKsPacketsLock.acquire()
            arrayToBeLooped += self.pendingACKsPackets
            self.pendingACKsPackets = []
            self.pendingACKsPacketsLock.release()

            packetsNotConfirmed = []# reset local array of loop

            # if len(arrayToBeLooped) != 0:
            #     sys.stdout.write("gonna loop these")
            #     for packet in arrayToBeLooped:
            #         sys.stdout.write(str(packet.ack)+" "+str(packet.addressPortTuple)+", ")
            #     print ""

            for packet in arrayToBeLooped:
                if self.ACKManager.isACKConfirmed(packet.addressPortTuple,packet.ack):
                    print "got the ack: ", packet.ack
                    continue
                if time.time() - packet.lastTimeSent >=0.5:
                    print "didn't get the ack sending again: ", packet.ack
                    self.sock.sendto(json.dumps(packet.msg), packet.addressPortTuple)
                packetsNotConfirmed.append(packet)
            #end of for

            # if len(packetsNotConfirmed) != 0:
            #     sys.stdout.write("packetsNotConfirmed=")
            #     for packet in packetsNotConfirmed:
            #         sys.stdout.write(str(packet.ack)+" "+str(packet.addressPortTuple)+", ")
            #     print ""
            arrayToBeLooped = packetsNotConfirmed
            time.sleep(0.5)
        #end of while
    #end __waitingForAcks


    def recvfrom(self,buffer=1024):
        with self.recvMsgsCV:#
            while self.recvMsgsQ.empty():# just wait while its empty
                print "Socket||recvfrom||waiting for a new msg"
                self.recvMsgsCV.wait()
                print "Socket||recvfrom||done waiting for a new msg"

            msg,addressPortTuple = self.recvMsgsQ.get()
        #done with self.recvMsgsCV
        
        
        return msg,addressPortTuple
    #end recv

    def __listen(self):
        while True:
            print "Socket||__listen||waiting for new msg"
            recv,addressPortTuple = self.sock.recvfrom(1024)
            try:
                recvJ = json.loads(recv)
            except:
                print "Socket||__listen||got non json object:"+recv
                recvJ = {"msg": recv}

            if recvJ.get("msg","") == "ack": # I'm receiving an ack to a message I sent
                print "Socket||__listen||im receiving an ack"
                self.ACKManager.confirmACK(addressPortTuple,int(recvJ["ack"]))
                continue

            else:# then it's a message intended to me, I better reply to it
                #first: just send the ack
                sendJ={ "msg" : "ack", "ack" : recvJ["ack"] }
                self.sock.sendto(json.dumps(sendJ),addressPortTuple)
                print "Socket||__listen||sending ACK back,"+json.dumps(sendJ)

                #second: see if we already have it just skip ... we don't want to process it twice, do we?
                if addressPortTuple in self.recvACKs.keys() and recvJ["ack"] in self.recvACKs.get(addressPortTuple):
                    print "Socket||__listen||we already have that, Skipping..."
                    continue

                #third: oh, looks like it wasn't processed before, we better mark it as proccessed then
                if addressPortTuple not in self.recvACKs.keys():
                    self.recvACKs.put(addressPortTuple,[ recvJ["ack"] ] )
                else:
                    self.recvACKs.get(addressPortTuple).append( recvJ["ack"] )

                #fourth: and ofcourse, put it in the processing queue
                with self.recvMsgsCV:
                    self.recvMsgsQ.put( (recv,addressPortTuple) )
                    self.recvMsgsCV.notify()
        #now go back in the loop again!
    #end __listen

    def __startUpListeningThread(self):
        listenThread = threading.Thread(target = self.__listen)
        listenThread.name = "listenForAllMessages"
        listenThread.start()
    #end __startUpListeningThread

#end class Socket