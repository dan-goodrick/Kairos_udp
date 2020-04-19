#!/usr/bin/env python
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

class RX(DatagramProtocol):
    '''
    Listens on a port for messages
    If found, it decodes the message
    Updates values in the gui
    '''
    def datagramReceived(self, datagram, address):
        self.msg = datagram.decode('utf-8')
        print(self.msg)
        self.transport.write(datagram, address)

    def get_datagram(self):
        return self.msg


if __name__ == '__main__':
    reactor.listenUDP(7200, RX())
    reactor.run()
