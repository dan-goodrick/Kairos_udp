from twisted.internet import reactor, protocol, task
import time

class UDP_Protocol(protocol.DatagramProtocol):
    def __init__(self, host, port, reactor):
        self.host = host
        self.port = port
        self._reactor = reactor
        self.datagram = 'Hello_world'

    def startProtocol(self):
        self.transport.connect(self.host, self.port)

    def stopProtocol(self):
        #on disconnect
        self._reactor.listenUDP(0, self)

    def sendDatagram(self):
        # datagram = 'Hello world'.encode() #ntp_packet
        self.datagram+='!'
        try:
            self.transport.write(self.datagram.encode(), (self.host, self.port))
            # print( "{:0.6f}".format(time.time()))
        except Exception as e:
            print(e)
            pass
    def get_datagram(self, msg):
        self.datagram = msg

    def datagramReceived(self, datagram, host):
        print('Datagram received: ', repr(datagram))
        pass
        # self.sendDatagram()

def main():
    protocol = UDP_Protocol('127.0.0.1', 8000, reactor)
    t = reactor.listenUDP(0, protocol)
    protocol.get_datagram('Helloworld')
    l = task.LoopingCall(protocol.sendDatagram)
    l.start(1.0) # call every second
    reactor.run()

if __name__ == '__main__':
    main()
