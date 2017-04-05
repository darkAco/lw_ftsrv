"""
    Server for File Transfers (Custom Protocol)
    Server für Dateiübertragungen (Custom Protocol)
"""
import os.path
import platform
import pickle
import socket
import threading

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
        print("Running in a Java Virtual Environment")
    else:
        raise Exception("Operating System could not be determined. Exiting")
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
    while serving:
        # Await Connection        
        remoteSock, remoteAdr = sock.accept()
        print("Connection established from", remoteAdr)
        handling = True
        while handling:
            data = remoteSock.recv(1024)
            
    # Shutdown socket
    sock.close()
    print("Connection is closed.")
