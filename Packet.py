class Packet:
	def __init__(self, msg, ack, addressPortTuple, lastTimeSent):
		"""
		args:
			msg : any type
			ack : ack of the packet: int
			addressPortTuple: tuple of address,port
			lastTimeSent: float
		"""
		self.msg = msg
		self.ack = int(ack)
		self.addressPortTuple = addressPortTuple
		self.lastTimeSent = lastTimeSent
