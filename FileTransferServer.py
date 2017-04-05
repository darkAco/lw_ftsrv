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
from time import sleep

# Helper Functions // Hilfsfunktionen
def checkSocket(sock):
    testsock = socket.socket(sock.family, sock.type)
    adrtup = ('127.0.0.1', sock.getsockname()[1])
    print("Testing connection to", adrtup)
    retval = testsock.connect_ex(adrtup)
    print("Retval", retval)
    if retval is 0:
        testsock.shutdown(socket.SHUT_RDWR)
        testsock.close()
    del testsock
    return True if retval is 0 else False

def hashBytes(bytestring):
    return hashlib.sha256(bytestring).digest()

# Main-Function // Hauptroutine
if __name__ == '__main__':
    conf = dict()
    confpath = r'server.conf'
    opsys = platform.system()

    # I.: System Check
    if opsys is "Windows":
        print("Running on a Windows Machine")
    elif opsys is "Linux":
        print("Running on a Linux Machine")
    elif opsys is "Java":
        raise Exception("Running in a Java Virtual Environment is not supported (yet). Exiting.")
        exit(1)
    else:
        raise Exception("Operating System could not be determined. Exiting.")
        exit(1)

    # II.: Load Config
    # Config File is located under {script root path}\config.bin
    if os.path.exists(confpath):
        conf = pickle.load(open(confpath, 'rb'))
        print("Configuration file loaded")
    else:
        print("Configuration file was not found, using default config")
        conf = dict()
        conf.update({"L3PROT":"tcp"})
        conf.update({"HOSTNAME":"localhost"})
        conf.update({"HOSTIP":"127.0.0.1"})
        conf.update({"HOSTPORT":5555})
    for key in conf:
        print(key, ":\t", conf[key])

    # III.: Startup
    sock = None
    if conf["L3PROT"].lower() == "tcp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP)
    elif conf["L3PROT"].lower() == "udp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_IP)
    else:
        raise Exception("Could not parse L3-Protocol from config, exiting")
        exit(1)
    sockAdrTup = (conf["HOSTIP"], conf["HOSTPORT"])
    sock.bind(sockAdrTup)
    print("Socket bound at", sockAdrTup)
    
    # IV.: Main Serving Loop
    sock.listen(1)
    serving = True
    chunksize = conf["BUFFERSIZE"]
    greetings = ["Intellect is the Understanding of Knowledge.",
                 "Sentience is the Basest Form of Intellect.",
                 "Understanding is the True Path to Comprehension.",
                 "Comprehension is the Key to all Things.",
                 "The Omnissiah knows all, comprehends all.",
                 "The Soulless sentience is the enemy of all.",
                 "Flesh is Fallible, but Ritual Honours the Machine Spirit.",
                 "To Break with Ritual is to Break with Faith."]
    while serving:
        # Await Connection        
        remoteSock, remoteAdr = sock.accept()
        print("Connection established from", remoteAdr)
        handling = True
        try:
            while handling:
                if conf["L3PROT"].lower() == "tcp":
                    # Protocol dictates how handling has to be done for tcp
                    # 1. Client connects to server (done here)
                    # 2. Client sends (Server receives) ALL correct greetings hashed:
                    recv_greetings = []
                    for i in range(len(greetings)):
                        data = remoteSock.recv(64) # 64 is Fixed Size for greetings
                        msg = data.decode('utf-8')
                        print(msg, str(msg==greetings[i]))
                        recv_greetings.append(msg)
                    for i in range(len(greetings)):
                        if greetings[i] != recv_greetings[i]:
                            raise Exception("Incorrect greeting")
                    # Greeting phase succeeded here
                    connectionStanding = True
                    # 3. Wait for file requests or offers
                    while connectionStanding:
                        data = remoteSock.recv(64) # 64 is fixed size for commands
                        msg = data.decode('utf-8')
                        # Send or Receive File?
                        if "CliSend" == msg:
                            print("Receiving file from Client ...")
                            data = remoteSock.recv(512) # 512 is fixed size for path+filename
                            filepath = data.decode('utf-8')
                            data = remoteSock.recv(8)   # 8 Byte for boolean override True/False
                            override = bool(data.decode('utf-8'))

                            # Answer to client, confirmation to send file
                            if os.path.exists(filepath) and not override:
                                print("File already existing, not receiving.")
                                remoteSock.sendall("False".encode("utf-8"))
                            else: # can write
                                fh = open(filepath, 'wb+')
                        elif "SrvSend" == msg:
                            print("Sending file to Client ...")
                elif conf["L3PROT"].lower() == "udp":
                    raise Exception("Not yet implemented, use tcp for now.")
        except Exception as e:
            print("Error:", e)
        finally:
            remoteSock.close()
    # Shutdown socket
    sock.close()
    print("Connection is closed.")
