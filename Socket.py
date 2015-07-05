import socket
import threading
import Queue #synchronized queue
import json
import time #for sleeping 
from ACKManager import ACKManager
from Dict import Dict

class Socket:
	def __init__(self,port):
		self.sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		# self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT, 1)#so any socket can use this port
		self.sock.bind(('',port))

		self.msgsLock=threading.Lock()
		self.msgsCV=threading.Condition(self.msgsLock)
		self.msgsQ=Queue.Queue()#a queue of messages available to be returned through recv function

		self.recvACKS  = Dict() #ACKS[addressPortTuple] = [list of ACKS of messages that are received and proccessed]

		self.ACKManager = ACKManager() #manages acks for messages sent

		self.__startUpListeningThread()
	#end init	

	def sendto(self,msg,addressPortTuple):
		sendThread=threading.Thread(target=self.__sendto)
		sendThread.name="sendto"+json.dumps(addressPortTuple)
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
		while True:
			msg["ack"] = self.ACKManager.getACK(addressPortTuple)

			self.sock.sendto(msg,addressPortTuple)
			print "Socket||__sendto||sent and waiting 0.5, "+json.dumps(addressPortTuple)
			time.sleep(0.5)
			if self.ACKManager.isACKConfirmed(addressPortTuple,msg["ack"]):
				print "Socket||__sendto||got ack,"+json.dumps(addressPortTuple)
				break
			else:
				print "Socket||__sendto||didn't get ack,"+json.dumps(addressPortTuple)
				continue
	#end sendto

	def recvfrom(self,buffer=1024):
		with self.msgsCV:#
			while self.msgsQ.empty():# just wait while its empty
				print "Socket||recvfrom||waiting for a new msg"
				self.msgsCV.wait()
				print "Socket||recvfrom||done waiting for a new msg"

		#done with self.msgsCV
		msg,addressPortTuple = self.msgsQ.get()
		
		return msg,addressPortTuple
	#end recv

	def __listen(self):
		while True:
			print "Socket||__listen||waiting for new msg"
			recv,addressPortTuple=self.sock.recvfrom(1024)
			recvJ=json.loads(recv)

			if recvJ.get("msg","") == "ack":# if I'm receiving an ack, then it's an ack to a message i sent
				print "im receiving an ack"
				self.ACKManager.confirmACK(addressPortTuple,recvJ["ack"])
				continue

			else:# then it's a message intended to me, I better reply to it
				#first: just sent the ack
				sendJ={ "msg" : "ack", "ack" : recvJ["ack"] }
				self.sock.sendto(json.dumps(sendJ),addressPortTuple)
				print "Socket||__listen||sending ACK back,"+json.dumps(sendJ)

				#second: see if we already have it just skip ... we don't want to process it twice, do we?
				if addressPortTuple in self.recvACKS.keys() and recvJ["ack"] in self.recvACKS.get(addressPortTuple):
					print "Socket||__listen||we already have that, Skipping..."
					continue

				#third: oh, looks like it wasn't processed before, we better mark it as proccessed then
				if addressPortTuple not in self.recvACKS.keys():
					self.recvACKS.put(addressPortTuple,[ recvJ["ack"] ] )
				else:
					self.recvACKS.get(addressPortTuple).append( recvJ["ack"] )

				#fourth: and ofcourse, put it in the processing queue
				with self.msgsCV:
					self.msgsQ.put( (recv,addressPortTuple) )
					self.msgsCV.notify()
		#now go back in the loop again!
	#end __listen

	def __startUpListeningThread(self):
		listenThread=threading.Thread(target=self.__listen)
		listenThread.name="listenForAllMessages"
		listenThread.start()
	#end __startUpListeningThread

#end class Socket