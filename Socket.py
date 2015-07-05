import socket
import threading
import Queue #synchronized queue
import json
import time #for sleeping 
from ACKManager import ACKManager
import Dict

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
			time.sleep(0.5)
			if self.ACKManager.isACKConfirmed(addressPortTuple,msg["ack"]):
				break
			else:
				continue
	#end sendto

	def recv(self):
		with self.msgsCV:#
			while self.msgsQ.empty():# just wait while its empty
				print "recv||waiting for a new msg"
				self.msgsCV.wait()
				print "recv||done waiting for a new msg"

		#done with msgsCV
		msg,addressPortTuple = self.msgQ.get()
		
		return msg,addressPortTuple
	#end recv

	def __listen(self):
		while True:
			recv,addressPortTuple=self.sock.recv(1024)
			recvJ=json.loads(recv)

			if recvJ["msg"] == "ack":# if I'm receiving an ack, then it's an ack to a message i sent
				self.ACKManager.confirmACK(addressPortTuple,recvJ["ack"])
				continue

			else:# then it's a message intended to me, I better reply to it
				#first: just sent the ack
				sendJ={ "msg" : "ack", "ack" : recvJ["ack"] }
				self.sock.sendto(sendJ,addressPortTuple)

				#second: see if we already have it just skip ... we don't want to process it twice, do we?
				if addressPortTuple in self.recvACKS.keys() and recvJ["ack"] in self.recvACKS[addressPortTuple]:
					continue

				#third: oh, looks like it wasn't processed before, we better mark it as proccessed then
				if addressPortTuple not in self.recvACKS.keys():
					self.recvACKS.put(addressPortTuple,[recvJ["ack"]])
				else:
					self.recvACKS.get(addressPortTuple).append(recvJ["ack"])

				#fourth: and ofcourse, put it in the processing queue
				self.msgQ.put(recv,addressPortTuple)
				self.msgCV.notify()
		#now go back in the loop again!
	#end __listen

	def __startUpListeningThread(self):
		listenThread=threading.Thread(target=self.__listen)
		listenThread.name="listenForNewTTTPlayers"
		listenThread.start()
	#end __startUpListeningThread
#end class Socket