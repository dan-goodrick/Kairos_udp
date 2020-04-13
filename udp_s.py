from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor


class UDPClientProtocol(DatagramProtocol):
    def __init__(self, host, port):
       self.host = host
       self.port = port

    def startProtocol(self):
       # Called when transport is connected
       self.transport.connect(self.host, self.port)
       self.transport.write('initiate protocol') # pseudo code.

    def stopProtocol(self):
       print("I have lost connection and self.transport is gone!")
       # wait some time and try to reconnect somehow?

 t = reactor.listenUDP(0, UDPClientProtocol('127.0.0.1', 8000))
 reactor.run()
