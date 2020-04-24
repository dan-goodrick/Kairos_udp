import tkinter as tk
from tkinter import font
from mStreamingUDP import ParseStreamingUDP
from twisted.internet import tksupport, reactor
from twisted.internet.protocol import DatagramProtocol

class RX(DatagramProtocol):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.params = {}

    def datagramReceived(self, datagram, address):
        self.msg = datagram.decode('utf-8')
        self.widget.set(self.msg)  # update the label
        # print(self.params)
        #self.transport.write(datagram, address)  # cause recursive issue

class RX_GUI():
    def __init__(self, msg_dict):
        self.width = 15
        self.root = tk.Tk()
        self.root.protocol('WM_DELETE_WINDOW', self.quit)
        self.init_params(msg_dict)
        self.configure_port()
        # self.start_button()
        self.show_params()
        tksupport.install(self.root)
        self.quit_button()
        reactor.run()

    def configure_port(self):
        self.port_label = tk.Label(self.root,text="Enter Port #:", width=self.width )
        self.port_label.grid(column=0,  sticky = tk.E, row=1)
        self.port_label['font'] = font.Font(weight='bold')
        self.port_field = tk.Entry(self.root,width=self.width)
        self.port_field.grid(column=1, sticky = tk.W, row=1)
        self.port_field.insert(tk.END, '7200')
        self.msg = tk.StringVar()
        self.msg.set('')
        self.button = tk.Button(self.root, text="Start Listening",
                                command=self.start_listening, bg='green')
        self.button.grid(column=3, columnspan=2, row=1)

    def start_listening(self):
        self.rx_port = reactor.listenUDP(int(self.port_field.get()), RX(self.msg))

    def quit_button(self):
        self.quit_button = tk.Button(self.root,text="Exit",command=self.quit)
        self.quit_button.grid(columnspan = 4, sticky = tk.W+tk.E)
        self.quit_button['font'] = font.Font(size=16, weight='bold')

    def show_params(self, param_cnt=34):
        l = tk.Label(self.root,text=f"Message Parameters:" )
        l['font'] = font.Font(weight='bold', underline=1)
        l.grid(columnspan = 4, sticky = tk.W+tk.E,row=3)

        self.msg_lbl = tk.Label(self.root, textvariable=self.msg)
        self.msg_lbl.grid(row=4, columnspan=4)
        self.msg.trace('w', self.parse_msg)

    def init_params(self, msg_dict):
        self.labels = {}
        self.params = {}
        for key in msg_dict:
            if 'Reserved' in key:
                continue
            self.params[key] = tk.StringVar()
            self.params[key].set('')
            self.labels[key] = [tk.Label(self.root, text=f"{key}:"),
                                tk.Label(self.root, textvariable=self.params[key])]

    def parse_msg(self, *args):
        param_cnt=len(self.params)
        parsed_msg = ParseStreamingUDP(self.msg.get())
        row_offset = 6
        row = 0
        for key in self.params:
            row_num = row_offset + int(row%(param_cnt//2))
            col = int(row//(param_cnt//2))*2
            row+=1
            self.params[key].set(parsed_msg[key])
            self.labels[key][0].grid(column = col, row=row_num)
            self.labels[key][1].grid(column = col+1, row=row_num)

    def quit(self):
        reactor.stop()
        self.root.destroy()

if __name__ == "__main__":
    strmDict = {
            'Version': '1.0',
            'Type': 'CMD',
            'Name': '',
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
            'TimeStamp': '56837',
            'Valid': True,
            }
RX_GUI(strmDict)
