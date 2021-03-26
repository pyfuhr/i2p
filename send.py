import socket
from threading import Thread

sock = socket.socket()

sock.connect(('10.20.2.90', 5000))

def asend(s):
    while True:
        mes = str(socket.gethostname()) + ': ' + input()
        s.send(mes.encode())
        if mes.endswith('EXIT'):
            break

def arecv(s):
    while True:
        print(s.recv(1024).decode())

Thread(target=lambda: arecv(sock)).start()
Thread(target=lambda: asend(sock)).start()


#sock.close()
