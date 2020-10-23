#!/usr/bin/python3

import socket
import os
from sys import argv
import time



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

def encodeTrame(tabfile, Nseq): #Création de ma trame avec le bon format "numseqsur 6B"
    return str(Nseq).zfill(6).encode()+tabfile[Nseq-1]

IP = ""

localPort = int(argv[1]) #Port de connection en argument

bufferSize = 1024

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) #Socket de connection

UDPServerSocket.bind((IP,localPort))
ETAT = "Listen"
print("UDP server up and listening")
while (True):
    print("wait\n")
    data, addr = UDPServerSocket.recvfrom(bufferSize)  # buffer size is 1024 bytes
    event = data.decode("utf-8")[:-1] 
    if ETAT == "Listen" and event == "SYN":
        UDPServerSocket.sendto("SYN-ACK1050".encode(), addr)
        ETAT = "WAIT-ACK"
    elif ETAT == "WAIT-ACK" and event=="ACK":
        ETAT = "WAIT-TITRE"
        break


PortDATA = 1050

bufferSize = 1476

UDPDATA = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPDATA.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
UDPDATA.bind((IP,PortDATA))

siezeFile = 0
lastseq = 0
DATA = []
td = 0
tf = 0
while (True):
    #print("Envoie \n")
    if ETAT == "WAIT-TITRE":
        data, addr = UDPDATA.recvfrom(bufferSize)  # buffer size is 1024 bytes
        event = data.decode("utf-8")[:-1]
        siezeFile = os.path.getsize(event)
        ETAT = "SENDING"
        UDPDATA.sendto("000000".encode(),addr)
        UDPDATA.settimeout(0.5)
        DATA = fileToTab(event)
        print("la taille de ma donnée est {}\n".format(len(DATA)))
        td = time.time()
    elif ETAT == "SENDING":
        if lastseq == (len(DATA) - 1):
            print("condition FIN\n")
            for j in range(7):
                UDPDATA.sendto("FIN".encode(), addr)
                time.sleep(0.2)
            break
        for i in range(500):
            if i+lastseq+1 <= len(DATA):
                Trame = encodeTrame(DATA, i+lastseq+1)
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
debit = siezeFile/(tf-td)
print("LE debit de la data utile est de: {}B/s".format(debit))
