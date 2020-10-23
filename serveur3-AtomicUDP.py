#!/usr/bin/python3.8

import socket
import os
from sys import argv
import time
import threading




def fileToTab(fichier):
    file_data = []
    file = open(fichier, "rb")
    data_a_lire = file.read(1494)
    file_data.append(data_a_lire)
    while data_a_lire:
        data_a_lire = file.read(1494)
        file_data.append(data_a_lire)
    file.close()
    return file_data

def encodeTrame(tabfile, Nseq):
    return str(Nseq).zfill(6).encode()+tabfile[Nseq-1]

def sendfile(i):
    PortDATA = i
    print(i)

    bufferSize = 1476

    UDPDATA = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPDATA.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDPDATA.bind(("0.0.0.0", PortDATA))

    siezeFile = 0
    lastseq = 0
    DATA = []
    data, addr = UDPDATA.recvfrom(bufferSize)  # buffer size is 1024 bytes
    event = data.decode("utf-8")[:-1]
    #print(event)
    siezeFile = os.path.getsize(event)
    UDPDATA.sendto("000000".encode(), addr)
    DATA = fileToTab(event)
    print("la taille de nombre sequence est de: {}\n".format(len(DATA)))
    UDPDATA.settimeout(0.2)
    while (True):
        # print("Envoie \n")
            td = time.time()
            if lastseq == (len(DATA) - 1):
                print("condition FIN\n")
                for j in range(7):
                    UDPDATA.sendto("FIN".encode(), addr)
                    time.sleep(0.4)
                break
            for i in range(500):
                if i + lastseq + 1 <= len(DATA):
                    Trame = encodeTrame(DATA, i + lastseq + 1)
                    UDPDATA.sendto(Trame, addr)
            try:
                data, addr = UDPDATA.recvfrom(1020)
                Nseq = int(data.decode("utf-8")[3:9])
                if Nseq > lastseq:
                    lastseq = Nseq
            except socket.timeout:
                print("J'ai rien écouté ! \n")
                continue
    tf = time.time()
    debit = siezeFile / (tf - td)
    print("LE debit de la data utile est de: {}B/s".format(debit))


if __name__ == "__main__":

    IP = ""

    localPort = int(argv[1])

    IDclient = localPort + 1

    bufferSize = 1500

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDPServerSocket.bind((IP, localPort))
    nv_thread = threading.Thread(target = sendfile, args=(IDclient,))
    nv_thread.start()

    print("UDP server up and listening")
    while (True):
        print("wait\n")
        data, addr = UDPServerSocket.recvfrom(bufferSize)  # buffer size is 1024 bytes
        #print(data.decode("utf-8"))
        event = data.decode("utf-8")[:-1]
        msg = "SYN-ACK"+str(IDclient)
        UDPServerSocket.sendto(msg.encode(), addr)
        IDclient += 1
        nv_thread = threading.Thread(target = sendfile, args=(IDclient,))
        nv_thread.start()
