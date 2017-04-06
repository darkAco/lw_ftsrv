"""
    Server for File Transfers (Custom Protocol)
    Server für Dateiübertragungen (Custom Protocol)
"""
import os.path
import platform
import pickle
import socket
import threading
import hashlib
import time
import random

"""
    Helper Functions // Hilfsfunktionen
"""
# Calculates the hash value of the given bytes // Berechnet den Hashwert der Bytefolge
def hashBytes(bytestring):
    hashlib.sha256()
    return hashlib.sha256(bytestring).digest()

# Encodes the bytestring "message" with "key" by applying Vigenère encryption
# Warning: Insecure Encryption! This is only used for obfuscation
def encodedBytes(key, message):
    res = []
    for i in range(len(message)):
        key_c = key[i % len(key)]
        res.append(chr(ord(message[i]) + ord(key_c) % 256))
    return "".join(res)

# Check if the executing OS is compatible 
def syscheck():
    if platform.system() != "Windows" and platform.system() != "Linux":
        raise Exception("[ERROR]\tOperating System could not be determined. Exiting.")
        exit(1)

# Loads the (relative) local config file
def loadConfig(confpath=r'ftsrv.conf'):
    conf = dict()
    if os.path.exists(confpath):
        conf = pickle.load(open(confpath, 'rb'))
        print("[INFO]\tConfiguration file loaded")
    else:
        print("[INFO]\tConfiguration file was not found, using default config")
        conf = dict()
        conf.update({"L3PROT":"tcp"})
        conf.update({"HOSTNAME":"localhost"})
        conf.update({"HOSTIP":"127.0.0.1"})
        conf.update({"HOSTPORT":5555})
    for key in conf:
        print(key, ":\t", conf[key])
    return conf

# Processes a customary three way handshake with the client
# (only to be called on active connections)
def ThreeWayHandshake(clSock, clAdr):
    # Step 1
    data = clSock.recv(2024).decode('utf-8')
    # Check correct greeting (ServerHostname)
    if data != socket.gethostname() or not data:
        raise Exception("[ERROR]\tHandshake Failed at Step 1 ("+data+"!="+socket.gethostname()+")")
    else:
        print("[INFO]\tHandshake Step 1 ok")
    # Step 2
    # Get random session key from client hash:
    r = random.Random()
    clSeed = hashBytes((clAdr[0]+str(time.time())).encode('utf-8'))
    r.seed(clSeed)
    sessionKey = ""
    for i in range(256):
        sessionKey += chr(r.getrandbits(8))
    try:
        print("[DEBUG]\tSessionKey:"+sessionKey)
        print("[DEBUG]\tSeed:"+clSeed.decode('utf-8'))
    except Exception:
        pass
    # Send sessionkey to Client
    clSock.send(str(sessionKey).encode('utf-8'))
    print("[INFO]\tHandshake Step 2 ok")
    # Step 3
    data = clSock.recv(2024).decode('utf-8')
    # Check correct session key Confirmation (encoded ServerHostname)
    enc_hostname = encodedBytes(str(sessionKey), str(socket.gethostname()))
    if data != enc_hostname or not data:
        raise Exception("[ERROR]\tHandshake Failed at Step 3 ("+data+"!="+enc_hostname+")")
    else:
        print("[INFO]\tHandshake Step 3 ok\n[INFO]\tHandshake finished")

# Main-Function // Hauptroutine
if __name__ == '__main__':
    # Load config
    conf = loadConfig()
    # Create socket
    sock = None
    if conf["L3PROT"].lower() == "tcp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP)
    elif conf["L3PROT"].lower() == "udp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_IP)
    else:
        raise Exception("[ERROR]\tCould not parse L3-Protocol from config, exiting")
        exit(1)
    sockAdrTup = (conf["HOSTIP"], conf["HOSTPORT"])
    sock.bind(sockAdrTup)
    print("[INFO]\tSocket created and bound at", sockAdrTup)
    
    # Listen on Socket
    sock.listen(1)
    while True:
        print("[INFO]\tawaiting Connection ..")
        remoteSock, remoteAdr = sock.accept()
        print("[INFO]\tConnection established from", remoteAdr)
        handling = True
        try:
            while handling:
                if conf["L3PROT"].lower() == "tcp":
                    # Server greets Client with Version hash
                    # Build up Connection (Handshake)
                    ThreeWayHandshake(remoteSock, remoteAdr)
                    raise Exception("[DEBUG]\tExiting after successful Three-Way-Handshake")
                
                elif conf["L3PROT"].lower() == "udp":
                    raise Exception("[ERROR]\tUDP is not yet implemented, use tcp for now.")
        except Exception as e:
            print(str(time.time()) + "\n" + str(e))
        finally:
            remoteSock.close()
    # Shutdown socket
    sock.close()
    print("Connection is closed.")
