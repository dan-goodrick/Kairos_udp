import tkinter as tk
from twisted.internet import tksupport, reactor
from twisted.internet.protocol import DatagramProtocol
msg = ''

class RX(DatagramProtocol):
    def datagramReceived(self, datagram, address):
        global msg
        msg = datagram.decode('utf-8')
        self.transport.write(datagram, address)

class RX_GUI():
    def __init__(self):
        self.root = tk.Tk()
        self.show_message()
        tksupport.install(self.root)
        self.reactor = reactor.listenUDP(7201, RX())
        reactor.run()
        self.root.after(1000, self.show_message)
        self.root.mainloop()

    def show_message(self):
        global msg
        print(msg)
        self.msg = tk.Label(self.root,text=msg, width=20)
        self.msg.grid(row=0)
        self.root.after(1000, self.show_message)
        
RX_GUI()
