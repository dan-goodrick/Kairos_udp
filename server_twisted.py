#!/usr/bin/env python
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

class ServeUDP(DatagramProtocol):
    '''
    Listens on a port for messages
    If found, it decodes the message
    Updates values in the gui
    '''
    def datagramReceived(self, datagram, address):
        self.datagram = datagram
        print(self.datagram)
        self.transport.write(datagram, address)

    def get_datagram(self):
        return self.datagram

def main():
    reactor.listenUDP(7201, ServeUDP())
    reactor.run()

if __name__ == '__main__':
    main()
