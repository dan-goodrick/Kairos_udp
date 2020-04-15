from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, task, protocol
from mStreamingUDP import Client_UDP, BuildStreamingUDP, valid_IP, get_checksum
import time

class Client_UDP(protocol.DatagramProtocol):
    '''Starts a socket with server.
       Gets the values of strmDict
       Builds a message according to the protocol
       sends message to the host and port
       repeats every .1 seconds
       stops when protocol is finished'''
    def __init__(self, host, port, reactor):
        self.host = host
        self.port = port
        self._reactor = reactor
        self.datagram = 1

    def startProtocol(self):
        self.transport.connect(self.host, self.port)

    def sendDatagram(self):
        self.datagram = time.time()#BuildStreamingUDP(strmDict) #figure out how to get values from a GUI
        if self.datagram:
            try:
                self.transport.write(str(self.datagram).encode(), (self.host, self.port))
            except Exception as e:
                print(e)
        else:
            print(f"Error: {self.datagram} is not a valid message")

    def datagramReceived(self, datagram, host):
        pass

def main():
    protocol = Client_UDP('127.0.0.1', 7201, reactor)
    reactor.listenUDP(0, protocol)
    l = task.LoopingCall(protocol.sendDatagram)
    l.start(1.0) # call every second
    reactor.run()
    protocol.stopProtocol()

if __name__ == '__main__':
    main()
