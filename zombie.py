#coding: utf-8
#from os import fork, getppid, wait
from sys import exit
from time import sleep
import socket, sys
import os

#comando para ver processos: ps -eo pid,ppid,stat,cmd
#comando mais simples: top

def receivemessage(socket):
    data = socket.recv(1024)
    if not data :
        print 'Connection closed'
        sys.exit()
    else :
        #print data
        sys.stdout.write("Server Response: " + data + "\n")
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
s.settimeout(2)
print "test"
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
        #data = client.recv(1024)
        data = receivemessage(s)
        #Message Received
        #alive = self.onmessage(client, data, client_role)

except KeyboardInterrupt:
    # Fim do programa
    print "Disconnecting..."
    s.send("die")
    sys.exit()

            #    while i < 20:
            #        print "Caraio borracha"
            #        i += 1
            #        sleep(1)
