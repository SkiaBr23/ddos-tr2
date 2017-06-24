#coding: utf-8
#from os import fork, getppid, wait
from sys import exit
from time import sleep
import socket, sys
import os
import re

#comando para ver processos: ps -eo pid,ppid,stat,cmd
#comando mais simples: top

def receivemessage(socket):
    data = socket.recv(1024)
    if not data :
        print 'Connection closed'
        sys.exit()
    else :
        #print data
        sys.stdout.write("Server Response: " + data)
        return data

#pid = fork()
#i = 0
#if pid == 0:
#    exit("Child: Goodbye, cruel world")
#else:
    #print "Parent: I created a child with pid", pid,\
    #      "and now all I want to do is sleep..."

if(len(sys.argv) < 3) :
    print 'Usage : python zombie.py hostname port'
    sys.exit()

host = sys.argv[1]
port = int(sys.argv[2])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(None)
# connect to remote host
try :
    s.connect((host, port))
except :
    print 'Unable to connect'
    sys.exit()

print 'Connected to remote host'

alive = 1;
status = "Idle"
try:
    while alive:
        data = receivemessage(s)
        print data
        data2 = data.rstrip()
        if data2 == "die":
            s.send("die")
            alive = 0
        if data2.startswith("attack"):
            print "Attacking " + data2.split()[1] + " at port " + data2.split()[2]
        if data2 == "stop":
            print "Stop attacking"


except KeyboardInterrupt:
    # Fim do programa
    print "Disconnecting..."
    s.send("die")
    sys.exit()

            #    while i < 20:
            #        print "Caraio borracha"
            #        i += 1
            #        sleep(1)
