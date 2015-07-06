# from Dict import Dict
import threading

class ACKManager:

	def __init__(self):
		self.sentACKS = {}
		self.confirmedACKS = {}

		self.sentLock=threading.Lock()
		self.confirmedLock=threading.Lock()
	#end __init__

	def getACK(self,addressPortTuple):# call it when u send a message to get an ACK number, so you can include it in the msg
		self.sentLock.acquire()

		# get the maximum ack number of the list in the dictionary, if it doesnt exist then it's just 0
		ack = max( self.sentACKS.get(addressPortTuple,[-1])  ) + 1
		# now put it back in the list
		if self.sentACKS.get(addressPortTuple,None) == None:
			self.sentACKS[addressPortTuple] = [ack]
		else:
			self.sentACKS.get(addressPortTuple).append(ack)

		self.sentLock.release()

		return str(ack)
	#end getACK

	def confirmACK(self,addressPortTuple,ack):# call it when you have received an ACK and you want to confirm it
		ack = int(ack)

		self.confirmedLock.acquire()

		acks = self.confirmedACKS.get(addressPortTuple,None)

		if acks == None:
			self.confirmedACKS[addressPortTuple] = [ack]
		else:
			self.confirmedACKS.get(addressPortTuple).append(ack)

		self.confirmedLock.release()
	#end confirmACK

	def isACKConfirmed(self,addressPortTuple,ack):# call it when you want to check if ACK is confirmed
		ack = int(ack)

		self.confirmedLock.acquire()

		confirmedACKS = self.confirmedACKS.get(addressPortTuple,[])

		self.confirmedLock.release()

		return ack in confirmedACKS

		
#end ACK