import socket

sock = socket.socket()

sock.connect(('localhost', 5000))
print(sock.recv(1024).decode())
