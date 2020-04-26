import tkinter as tk
from tkinter import font
from datetime import date
import time
from twisted.internet import tksupport, reactor
from twisted.internet.protocol import DatagramProtocol

def get_checksum(string, num_digits=3):
    return abs(hash(string)) % (10 ** num_digits)
    
def ParseStreamingUDP(msg):
    #   Streaming Protocol Sample
    #   #|1.0|VEH_MHAFB1|CMD|123|45|56837|S,0|A,0|B,100|G,1|V,0|X,0,1,0,0,0,,,|Y,0,0,0,0,0,,,|Z,0,0,0,,,,,|C,XXX
    #   0   #                   Header
    #       |                   Delimiter
    #   1   1.0                 Message Version
    #   2   VEH_MHAFB1          Vehicle name
    #   3   CMD                 Command Message to Robotic Asset
    #   4   123                 Session ID
    #   5   45                  Message Sequence
    #   6   56837               Time stamp, ms from midnight
    #   7   0                   Steering Angle, Steering Wheel Centered
    #   8   0                   Throttle Percentage, 0%
    #   9   100                 Brake Percentage, 100%
    #   10  1                   Transmission state, 1=Park
    #   11  0                   Vehicle speed in mph
    #   12  Vehicle State       No Estop, No Pause, Enabled, Manual
    #   13  Vehicle Sequence    Not Initiating or shutting down, No Start, No Steering Cal, No Shifting
    #   14  Vehicle Mode        Progressive Steering, Progressive Braking, No Speed Control
    #   15  XXX                 Default Checksum
    parsed_UDP_msg = msg.split('|')
    # check that msg starts with a proper header character
    if parsed_UDP_msg[0] != '#':
        valid = False
    #verify checksum
    c,checksum = parsed_UDP_msg[15].split(',')
    if c == 'C':
        n = len(parsed_UDP_msg[15]) + 1#-n = start idx of checksum in msg
        chk = get_checksum(msg[:-n])
        if checksum.upper() == 'XXX' or chk == int(checksum):
            valid = True
        else:
            valid = False
    else:
        valid = False
    # populate the stream_in_dictionary
    strminDict = {}
    strminDict['Checksum'] = checksum
    strminDict['Version'] = parsed_UDP_msg[1]
    strminDict['Name'] = parsed_UDP_msg[2]
    strminDict['Type'] = parsed_UDP_msg[3]
    strminDict['Session'] = parsed_UDP_msg[4]
    strminDict['Sequence'] = parsed_UDP_msg[5]
    strminDict['TimeStamp'] = parsed_UDP_msg[6]

    # Get the steering command
    c,val = parsed_UDP_msg[7].split(',')
    if c == 'S':
        strminDict['Steering'] = int(val)
    else:
        valid = False

    # Get the throttle command
    c,val = parsed_UDP_msg[8].split(',')
    if c == 'A':
        strminDict['Throttle'] = int(val)
    else:
        valid = False

    # Get the break command
    c,val = parsed_UDP_msg[9].split(',')
    if c == 'B':
        strminDict['Brake'] = int(val)
    else:
        valid = False

    # Get the transission state (1=Parked)
    c,val = parsed_UDP_msg[10].split(',')
    if c == 'G':
        strminDict['Trans'] = int(val)
    else:
        valid = False

    # Get the velocity
    c,val = parsed_UDP_msg[11].split(',')
    if c == 'V':
        strminDict['Velocity'] = int(val)
    else:
        valid = False

    #break out the state parameters
    state_list = parsed_UDP_msg[12].split(',')
    if state_list.pop(0) == 'X':
        strminDict['State_Estop'] = state_list[0]
        strminDict['State_Paused'] = state_list[1]
        strminDict['State_Enable'] = state_list[2]
        strminDict['State_Manual'] = state_list[3]
        strminDict['State_L1'] = state_list[4]
        strminDict['State_L2'] = state_list[5]
        strminDict['State_Motion'] = state_list[6]
        strminDict['State_Reserved7'] = state_list[7]
    else:
        valid = False

    #break out the process parameters
    process_list = parsed_UDP_msg[13].split(',')
    if process_list.pop(0) == 'Y':
        strminDict['Process_Operation']=process_list[0]
        strminDict['Process_Shutdown']=process_list[1]
        strminDict['Process_Start']=process_list[2]
        strminDict['Process_SteeringCal']=process_list[3]
        strminDict['Process_TransShift']=process_list[4]
        strminDict['Process_Reserved5']=process_list[5]
        strminDict['Process_Reserved6']=process_list[6]
        strminDict['Process_Reserved7']=process_list[7]
    else:
        valid = False

    #break out the mode parameters
    mode_list = parsed_UDP_msg[14].split(',')
    if mode_list.pop(0) == 'Z':
        strminDict['Mode_ProgressiveSteeringDisable']=mode_list[0]
        strminDict['Mode_ProgressiveBrakingDisable']=mode_list[1]
        strminDict['Mode_VelocityControlEnable']=mode_list[2]
        strminDict['Mode_Reserved3']=mode_list[3]
        strminDict['Mode_Reserved4']=mode_list[4]
        strminDict['Mode_Reserved5']=mode_list[5]
        strminDict['Mode_Reserved6']=mode_list[6]
        strminDict['Mode_Reserved7']=mode_list[7]
    else:
        valid = False
    strminDict['Valid'] = valid
    return strminDict

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
        self.button.destroy()
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
