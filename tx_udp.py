import tkinter as tk
from tkinter import font
from collections import defaultdict
import socket
from datetime import date
import time

def get_checksum(string, num_digits=3):
    return abs(hash(string)) % (10 ** num_digits)

def BuildStreamingUDP(strmDict):
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

    TimeStamp = int((time.time() - time.mktime(date.today().timetuple()))*1000)
    msg = []
    msg.append('#') # Header
    msg.append(strmDict['Version']) #Version
    msg.append(strmDict['Name']) # Vehicle Name
    msg.append(strmDict['Type']) # Message Type
    msg.append(str(strmDict['Session'])) #Session ID
    msg.append(str(strmDict['Sequence'])) #Message Number
    msg.append(str(TimeStamp))
    msg.append(','.join(['S', str(strmDict['Steering'])]))
    msg.append(','.join(['A', str(strmDict['Throttle'])]))
    msg.append(','.join(['B', str(strmDict['Brake'])]))
    msg.append(','.join(['G', str(strmDict['Trans'])]))
    msg.append(','.join(['V', str(strmDict['Velocity'])]))
    msg.append(','.join(['X', str(strmDict['State_Estop']),
                              str(strmDict['State_Paused']),
                              str(strmDict['State_Manual']),
                              str(strmDict['State_Enable']),
                              str(strmDict['State_L1']),
                              str(strmDict['State_L2']),
                              str(strmDict['State_Motion']),
                              str(strmDict['State_Reserved7'])]))
    msg.append(','.join(['Y',str(strmDict['Process_Operation']),
                             str(strmDict['Process_Shutdown']),
                             str(strmDict['Process_Start']),
                             str(strmDict['Process_SteeringCal']),
                             str(strmDict['Process_TransShift']),
                             str(strmDict['Process_Reserved5']),
                             str(strmDict['Process_Reserved6']),
                             str(strmDict['Process_Reserved7'])]))
    msg.append(','.join(['Z',str(strmDict['Mode_ProgressiveSteeringDisable']),
                             str(strmDict['Mode_ProgressiveBrakingDisable']),
                             str(strmDict['Mode_VelocityControlEnable']),
                             str(strmDict['Mode_Reserved3']),
                             str(strmDict['Mode_Reserved4']),
                             str(strmDict['Mode_Reserved5']),
                             str(strmDict['Mode_Reserved6']),
                             str(strmDict['Mode_Reserved7'])]))
    chk = get_checksum('|'.join(msg))
    msg.append(','.join(['C',str(chk)]))
    return '|'.join(msg)

def valid_IP(ip):
    segs = ip.split('.')
    if len(segs) != 4:
        return False
    for seg in segs:
        if len(seg) > 3:
            return False
        if not seg.isnumeric():
            return False
        if int(seg) < 0  or int(seg) >= 256:
            return False
    return True

class GUI():
    def __init__(self, strmDict, freq=500):
        self.running = False
        self.w = 25
        self.strmDict = strmDict
        self.dict_labels = defaultdict()
        self.dict_fields = defaultdict()
        self.non_config_params = ['TimeStamp', "Checksum", 'Valid', 'Name']
        self.freq = freq
        self.ip = '127.0.0.1'
        self.port = 7200
        self.root = tk.Tk()
        self.root.protocol('WM_DELETE_WINDOW', self.quit)
        self.build_frame()
        self.configure_params()
        self.configure_msg()
        self.quit_button = tk.Button(self.root,text="Exit",command=self.quit)
        self.quit_button.grid(columnspan = 4, sticky = tk.W+tk.E,)
        self.quit_button['font'] = font.Font(size=16, weight='bold')

        self.root.after(self.freq, self.send_message)  # After 1 second, call send_message
        self.root.mainloop()

    def build_frame(self):
        self.root.title("Configure UDP Message")
        self.app = tk.Frame(self.root)
        self.app.grid()
        self.state = tk.StringVar()
        self.state.set("Start Sending") # initial Button text
        self.button = tk.Checkbutton(self.root,
                                     onvalue="Stop Sending",
                                     offvalue="Start Sending",
                                     indicatoron=False,
                                     variable=self.state, #enables var.get
                                     textvariable=self.state, #prints onvalue/offvalue on button
                                     command=self.toggle)
        self.button.grid(columnspan = 4, sticky = tk.W+tk.E,)
        self.button['font'] = font.Font(size=20, weight='bold')


    def configure_params(self):
        self.ip_label = tk.Label(self.root,text="IP Address:", anchor="e", width=self.w )
        self.ip_label.grid(column=0, columnspan = 2, sticky = tk.E, row=2)
        self.ip_label['font'] = font.Font(weight='bold')
        self.ip_field = tk.Entry(self.root,width=self.w )
        self.ip_field.insert(tk.END, self.ip)
        self.ip_field.grid(column=2, columnspan = 2, sticky = tk.W, row=2)

        self.port_label = tk.Label(self.root,text="Port #:", anchor="e", width=self.w )
        self.port_label.grid(column=0, columnspan = 2, sticky = tk.E, row=3)
        self.port_label['font'] = font.Font(weight='bold')
        self.port_field = tk.Entry(self.root,width=self.w )
        self.port_field.insert(tk.END, self.port)
        self.port_field.grid(column=2, columnspan = 2, sticky = tk.W, row=3)

        self.freq_label = tk.Label(self.root,text="Message Frequency (ms):", anchor="e", width=self.w )
        self.freq_label.grid(column=0, columnspan = 2, sticky = tk.E, row=4)
        self.freq_label['font'] = font.Font(weight='bold')
        self.freq_field = tk.Entry(self.root,width=self.w )
        self.freq_field.insert(tk.END, self.freq)
        self.freq_field.grid(column=2, columnspan = 2, sticky = tk.W, row=4)
        l = tk.Label(self.root,text=f"Message Parameters:" )
        l['font'] = font.Font(weight='bold', underline=2)
        l.grid(columnspan = 4, sticky = tk.W+tk.E,row=5)

    def configure_msg(self, row_offset=6, param_cnt=26):
        row = 0
        for key in self.strmDict:
            # Nonconfigurable parameters are not displayed in the GUI
            if 'Reserved' in key or key in self.non_config_params:
                continue
            row_num = row_offset + int(row%(param_cnt//2))
            col = int(row//(param_cnt//2))*2
            row+=1
            if key == 'Type': #with a refresh button, I could dynamically choose which Name to show in the congig window
                self.dict_labels[key] = tk.Label(self.root,text=f"{key} ('STS', or 'CMD'):", anchor="e", width=self.w )
            elif key == 'SelectedName':
                self.dict_labels[key] = tk.Label(self.root,text=f"{key} (If Type=='CMD'):", anchor="e", width=self.w )
            elif key == 'VehicleName':
                self.dict_labels[key] = tk.Label(self.root,text=f"{key} (If Type=='STS'):", anchor="e", width=self.w )
            else:
                self.dict_labels[key] = tk.Label(self.root,text=f"{key}:", anchor="e", width=self.w )
            self.dict_labels[key].grid(column=col, row=row_num)
            self.dict_fields[key] = tk.Entry(self.root,width=self.w )
            self.dict_fields[key].insert(tk.END, self.strmDict[key])
            self.dict_fields[key].grid(column=col+1, row=row_num)

    def send_message(self):
        if self.running:
            self.strmDict['Sequence']=int(self.strmDict['Sequence']) + 1
            self.dict_fields['Sequence'].delete(0, tk.END)
            self.dict_fields['Sequence'].insert(0, self.strmDict['Sequence'])
            self.build_msg()
            sock = socket.socket(socket.AF_INET, # Internet
                                 socket.SOCK_DGRAM) # UDP
            sock.sendto(self.msg.encode(), (self.ip, self.port))
        # After freq milliseconds, call send_message again (create a recursive loop)
        self.root.after(self.freq, self.send_message)

    def update_params(self):
        if valid_IP(self.ip_field.get()):
            self.ip = self.ip_field.get()
        if self.port_field.get().isnumeric():
            self.port = int(self.port_field.get())
        if self.freq_field.get().isnumeric():
            self.freq = int(self.freq_field.get())
        for key in strmDict.keys():
            if 'Reserved' in key or key in self.non_config_params:
                continue
            if key == 'Type':
                if strmDict['Type'] == 'STS':
                    self.strmDict['Name'] = self.dict_fields['VehicleName'].get()
                elif strmDict['Type'] == 'CMD':
                    self.strmDict['Name'] = self.dict_fields['SelectedName'].get()
            self.strmDict[key] = self.dict_fields[key].get()


    def build_msg(self):
        self.msg = BuildStreamingUDP(self.strmDict)
        row = self.quit_button.grid_info()['row'] + 1
        self.freq_label = tk.Label(self.root,text=f"Message:{self.msg}", anchor="e", width=self.w*4 )
        self.freq_label.grid(columnspan = 4, sticky = tk.W+tk.E, row=row)
        self.freq_label['font'] = font.Font(weight='bold')

    def toggle(self):
        if self.state.get() == "Stop Sending":
            print("turning on...")
            print (f"IP: {self.ip}")
            print (f"Port: {self.port}")
            print (f"Freq: {self.freq}")
            self.running = True
            self.update_params()
            self.build_msg()
        else:
            print("turning off...")
            self.running = False
            self.configure_params()
            self.configure_msg()
    def quit(self):
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
