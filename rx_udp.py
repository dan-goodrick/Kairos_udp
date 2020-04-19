import tkinter as tk
from tkinter import font
from collections import defaultdict
# from mStreamingUDP import BuildStreamingUDP
from twisted.internet import tksupport, reactor
from twisted.internet.protocol import DatagramProtocol

msg = ''
class RX(DatagramProtocol):
    '''
    Listens on a port for messages
    If found, it decodes the message
    Updates values in the gui
    '''
    #How do I get this out of here?
    def datagramReceived(self, datagram, address):
        global msg
        msg = datagram.decode('utf-8')
        self.transport.write(datagram, address)

class GUI():
    def __init__(self, strmDict):
        self.listening = False
        self.w = 40
        self.port = 7200
        self.root = tk.Tk()
        self.freq = 10
        tksupport.install(self.root)
        # self.reactor = reactor.listenUDP(self.port, RX())
        self.build_frame()
        self.configure_UDP()
        self.quit_button = tk.Button(self.root,text="Exit",command=self.quit)
        self.quit_button.grid(columnspan = 2, sticky = tk.W+tk.E, row=7)
        self.quit_button['font'] = font.Font(size=16, weight='bold')
        reactor.run()
        self.root.after(self.freq, self.show_message)
        self.root.mainloop()

    def build_frame(self):
        self.root.title("Listen for UDP Messages")
        self.app = tk.Frame(self.root)
        self.app.grid()
        self.state = tk.StringVar()
        self.state.set("Start Listening") # initial Button text
        self.button = tk.Checkbutton(self.root,
                                     onvalue="Stop Listening",
                                     offvalue="Start Listening",
                                     indicatoron=False,
                                     variable=self.state, #enables var.get
                                     textvariable=self.state, #prints onvalue/offvalue on button
                                     command=self.toggle)
        self.button.grid(column=0, columnspan=2, row=0, sticky = tk.W+tk.E,)
        self.button['font'] = font.Font(size=20, weight='bold')


    def configure_UDP(self):
        self.port_label = tk.Label(self.root,text="Port #:", anchor="e", width=self.w )
        self.port_label.grid(column=0, sticky = tk.E, row=2)
        self.port_label['font'] = font.Font(weight='bold')
        self.port_field = tk.Entry(self.root,width=self.w )
        self.port_field.insert(tk.END, self.port)
        self.port_field.grid(column=1, sticky = tk.W, row=2)

        self.freq_label = tk.Label(self.root,text="Message Frequency (ms):", anchor="e", width=self.w )
        self.freq_label.grid(column=0, sticky = tk.E, row=3)
        self.freq_label['font'] = font.Font(weight='bold')
        self.freq_field = tk.Entry(self.root,width=self.w )
        self.freq_field.insert(tk.END, self.freq)
        self.freq_field.grid(column=1, sticky = tk.W, row=3)

        l = tk.Label(self.root,text=f"Message Parameters:" )
        l['font'] = font.Font(weight='bold', underline=2)
        l.grid(columnspan = 4, sticky = tk.W+tk.E,row=5)

    def show_message(self):
        global msg
        if self.listening:
            self.msg = tk.Label(self.root,text=msg, anchor="w", width=self.w*2 )
            self.msg.grid(column=0, columnspan=2, sticky = tk.W, row=6)
            self.root.after(1000, self.show_message)

    def update_params(self):
        if self.port_field.get().isnumeric():
            self.port = int(self.port_field.get())
        if self.freq_field.get().isnumeric():
            self.freq = int(self.freq_field.get())

    def toggle(self):
        if self.state.get() == "Stop Listening":
            print("Listening...")
            self.listening = True
            # self.reactor.startListening()
            self.reactor = reactor.listenUDP(self.port, RX())
            self.update_params()
            self.show_message()
            # self.datagramReceived()
        else:
            print("turning off...")
            self.listening = False
            self.reactor.stopListening()
            # self.configure_UDP()
            # self.root.reactor('WM_DELETE_WINDOW', reactor.stop)


    def quit(self):
        reactor.stop()
        self.root.destroy()


if __name__ == "__main__":
    strmDict = {
            'Version': '1.0',
            'Type': 'CMD',
            'VehicleName':'VehicleName',
            'SelectedName': 'SelectedName',
            'Session': '123',
            'Sequence': '45',
            'Steering': 0,
            'Throttle': 0,
            'Brake': 100,
            'Trans': 1,
            'Velocity': 0,
            'State_Estop': '0',
            'State_Paused': '1',
            'State_Manual': '0',
            'State_Enable': '0',
            'State_L1': '0',
            'State_L2': '',
            'State_Motion': '',
            'State_Reserved7': '',
            'Process_Operation': '0',
            'Process_Shutdown': '0',
            'Process_Start': '0',
            'Process_SteeringCal': '0',
            'Process_TransShift': '0',
            'Process_Reserved5': '',
            'Process_Reserved6': '',
            'Process_Reserved7': '',
            'Mode_ProgressiveSteeringDisable': '0',
            'Mode_ProgressiveBrakingDisable': '0',
            'Mode_VelocityControlEnable': '0',
            'Mode_Reserved3': '',
            'Mode_Reserved4': '',
            'Mode_Reserved5': '',
            'Mode_Reserved6': '',
            'Mode_Reserved7': '',
            'Checksum': 'XXX',
            'Name': '',
            'TimeStamp': '56837',
            'Valid': True,
            }
    window = GUI(strmDict)

# UDP_IP = "127.0.0.1"
# UDP_PORT = 7200
#
# sock = socket.socket(socket.AF_INET, # Internet
#                      socket.SOCK_DGRAM) # UDP
# sock.bind((UDP_IP, UDP_PORT))
#
# while True:
#     data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
#     print ("received message:", data)
# (Pdb) self.reactor.reactor.running = True or False
