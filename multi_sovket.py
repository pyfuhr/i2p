from socket import socket
from threading import Thread
import socket as sock
# from time import sleep

def potok(sc: socket):
	print(sc.recv(1024).decode())
	sc.send(str(sc).encode())
	sc.close()

s = socket(sock.SO_REUSEADDR)
s.bind(('', 4040))
s.listen(100)

while True:
	sk, b = s.accept()
	Thread(target=lambda: potok(sk)).start()
