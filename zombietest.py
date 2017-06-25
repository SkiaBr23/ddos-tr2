#coding: utf-8
from os import fork, getppid, wait
from sys import exit
from time import sleep
import socket, sys
import os
import re

#comando para ver processos: ps -eo pid,ppid,stat,cmd
#comando mais simples: top


pid = fork()

if pid == 0:
    exit("Child: Goodbye, cruel world")
else:
    print "Parent: I created a child with pid", pid,\
          "and now all I want to do is sleep..."
    while True:
        print "Caraio borracha"
        sleep(1)
