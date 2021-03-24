import socket

sock = socket.socket()

sock.connect(('10.20.2.90', 5000))
print(sock.recv(1024).decode())

while True:
    mes = str(socket.gethostname()) + ': ' + input()
    sock.send(mes.encode())
    if mes.endswith('EXIT'):
        break

sock.close()
