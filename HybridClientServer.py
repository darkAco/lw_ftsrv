import DiffieHellman as dh
import socket
import random
import time

def _confirmedSend(sock, data, buffer=4096):
    origdata = data
    print("Sending", str(data).encode('ascii'))
    sock.sendall(str(data).encode('ascii'))
    data = sock.recv(buffer)
    if int(data.decode('ascii')) != origdata:
        raise Exception("Sent data validation failed", data.decode('ascii'))
def _confirmedReceive(sock, buffer=4096):
    data = sock.recv(buffer)
    sock.sendall(data)
    return int(data.decode('ascii'))
    
def DiffieHellmanExchange(sock, sender=True, KeySize=2**10):
    # Exchange of P, G
    P, G, Key = None, None, None
    if sender:
        # 1. Generate Q, P, G, transfer P and G
        Q, P = dh.NextSchnorrPrime(random.getrandbits(KeySize), dh.Fermat)
        G = dh.GetGenerator(Q, P)
        _confirmedSend(sock, P)
        _confirmedSend(sock, G)
        print("P, G exchanged")
        # 2. Generate a "Private Key" Xa
        Xa = random.getrandbits(KeySize)
        # 3. Get "Public" from "Private Key"
        Ya = pow(G, Xa, P)
        # Share "Public Key", Receive "Public Key"
        _confirmedSend(sock, Ya)
        Yb = _confirmedReceive(sock)
        # 4. Calculate "Shared Key" from Yb and Xa
        Key = pow(Yb, Xa, P)
        return Key
    else:
        # 1. Receive P, G
        P = _confirmedReceive(sock)
        G = _confirmedReceive(sock)
        # 2. Generate "Private Key" Xb
        Xb = random.getrandbits(KeySize)
        # 3. Get "Public" from "Private Key"
        Yb = pow(G, Xb, P)
        # Share "Public Key", Receive "Public Key"
        Ya = _confirmedReceive(sock)
        _confirmedSend(sock, Yb)
        # 4.Calculate "Shared Key" form Y
        Key = pow(Ya, Xb, P)
        return Key

def Client(serverAddress, tryConnectLimit=1024):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for i in range(tryConnectLimit):
        try:
            client.connect((serverAddress, 5123))
            DiffieHellmanExchange(client, sender=False)
            print("DiffieHellman Exchange successfull(", (serverAddress, 5123), ")")
            client.close()
        except Exception as e:
            print("Trying to connect:", i, "/", tryConnectLimit)
            print(e)
        time.sleep(15)

def Server(listeningAddress):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind((listeningAddress, 5123))
    listener.listen()
    while True:
        try:
            client, clientIp = listener.accept()
            DiffieHellmanExchange(client)
            print("DiffieHellman Exchange successfull (", clientIp, ")")
            client.close()
        except Exception as e:
            print(e)
