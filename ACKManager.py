# from Dict import Dict
import threading

class ACKManager:

    def __init__(self):
        self.sentACKS = {}
        self.confirmedACKS = {}

        self.sentACKSLock=threading.Lock()
        self.confirmedACKSLock=threading.Lock()
    #end __init__

    def getACK(self,addressPortTuple):# call it when u send a message to get an ACK number, so you can include it in the msg
        self.sentACKSLock.acquire()

        # get the maximum ack number of the list in the dictionary, if it doesnt exist then it's just 0
        ack = max( self.sentACKS.get(addressPortTuple,[-1])  ) + 1
        # now put it back in the list
        if self.sentACKS.get(addressPortTuple,None) == None:
            self.sentACKS[addressPortTuple] = [ack]
        else:
            self.sentACKS.get(addressPortTuple).append(ack)

        self.sentACKSLock.release()

        return str(ack)
    #end getACK

    def confirmACK(self,addressPortTuple,ack):# call it when you have received an ACK and you want to confirm it
        ack = int(ack)
        self.confirmedACKSLock.acquire()
        acks = self.confirmedACKS.get(addressPortTuple,None)

        if acks == None:
            self.confirmedACKS[addressPortTuple] = [ack]
        else:
            self.confirmedACKS.get(addressPortTuple).append(ack)

        self.confirmedACKSLock.release()
    #end confirmACK

    def isACKConfirmed(self,addressPortTuple,ack):# call it when you want to check if ACK is confirmed
        ack = int(ack)
        self.confirmedACKSLock.acquire()
        confirmedACKS = self.confirmedACKS.get(addressPortTuple,[])
        self.confirmedACKSLock.release()

        return ack in confirmedACKS

    #TODO: to be used
    def disconnect(self,addressPortTuple): # call it when a client has disconnected to clean up memory

        self.confirmedACKSLock.acquire()
        del self.confirmedACKS[addressPortTuple]
        self.confirmedACKSLock.release()

        self.sentACKSLock.acquire()
        del self.sentACKS[addressPortTuple]
        self.sentACKSLock.release()
    #end disconnect

#end ACK