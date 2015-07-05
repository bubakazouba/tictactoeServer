# from Dict import Dict
import threading

class ACKManager:

	def __init__(self):
		self.sentACKS = {}
		self.confirmedACKS = {}
		self.lock=threading.Lock()
	#end __init__

	def getACK(self,addressPortTuple):# call it when u send a message to get an ACK number, so you can include it in the msg
		self.lock.acquire()

		# get the maximum ack number of the list in the dictionary, if it doesnt exist then it's just 0
		ack = max( self.sentACKS.get(addressPortTuple,[-1])  ) + 1
		# now put it back in the list
		self.sentACKS.put(addressPortTuple).append(ack)

		self.lock.release()

		return ack
	#end getACK

	def confirmACK(self,addressPortTuple,ack):# call it when you have received an ACK and you want to confirm it
		self.lock.acquire()

		acks = self.confirmedACKS.get(addressPortTuple,None)

		if acks == None:
			self.confirmedACKS[addressPortTuple] = [ack]
		else:
			self.confirmedACKS.get(addressPortTuple).append(ack)

		self.lock.release()
	#end confirmACK

	def isACKConfirmed(self,addressPortTuple,ack):# call it when you want to check if ACK is confirmed
		self.lock.acquire()

		confirmedACKS = self.confirmedACKS.get(addressPortTuple,[])

		self.lock.release()

		return ack in confirmedACKS

		
#end ACK