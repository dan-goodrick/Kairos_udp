#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

# Here's a UDP version of the simplest possible protocol
class ServeUDP(DatagramProtocol):
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
