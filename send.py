import socket
from threading import Thread
import rsa
from string import ascii_letters
from random import choice

sock = socket.socket()

def xor(data, key):
    x = bytearray()
    for i in range(len(data) // len(key)):
        q = data[i*len(key):(i+1)*len(key)]
        x += bytearray(a^b for a, b in zip(*map(bytearray, [q, key])))
    if len(data) % len(key) != 0:
        q = data[-(len(data) % len(key)):]
        x += bytearray(a^b for a, b in zip(*map(bytearray, [q, key[0:len(data) % len(key)]])))

    return x

sock.connect(('10.20.2.61', 5000))
x = sock.recv(1024).decode()
x = rsa.PublicKey(int(x.split()[0]), int(x.split()[1]))
key = ''.join([choice(ascii_letters) for i in range(8)]).encode()
sock.send(rsa.encrypt(key, x))

def asend(s):
    while True:
        mes = "PyFuhr" + ': ' + input()
        s.send(xor(bytearray(mes, encoding='UTF8'), key))
        if mes.endswith('EXIT'):
            exit()

def arecv(s):
    while True:
        print(xor(s.recv(1024), key).decode())


try:
    Thread(target=lambda: arecv(sock)).start()
    Thread(target=lambda: asend(sock)).start()

    while True:
        pass
except SystemExit:
        sock.close()
except ConnectionResetError:
        exit()

#sock.close()
