"""
1-receive player1
2-receive player2
1-send to player1 using a different socket
2-sent to player2 using a different socket
"""
import socket
sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
sock.bind(('',5005))
msg1,addressPortTuple1=sock.recvfrom(1024)
msg2,addressPortTuple2=sock.recvfrom(1024)
sock2=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock2.bind(('',5005))
sock2.sendto("you are 1",addressPortTuple1)
sock2.sendto("you are 2",addressPortTuple2)

