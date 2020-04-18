import tkinter as tk
from tkinter import font
from collections import defaultdict
from mStreamingUDP import BuildStreamingUDP
import socket

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
        self.state.set("Start UDP") # initial Button text
        self.button = tk.Checkbutton(self.root,
                                     onvalue="Stop UDP",
                                     offvalue="Start UDP",
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
            print (f"IP: {self.ip}")
            print (f"Port: {self.port}")
            print (f"Freq: {self.freq}")
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
        self.msg = BuildStreamingUDP(strmDict)
        row = self.quit_button.grid_info()['row'] + 1
        self.freq_label = tk.Label(self.root,text=f"Message:{self.msg}", anchor="e", width=self.w*4 )
        self.freq_label.grid(columnspan = 4, sticky = tk.W+tk.E, row=row)
        self.freq_label['font'] = font.Font(weight='bold')

    def toggle(self):
        if self.state.get() == "Stop UDP":
            print("turning on...")
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
        # if itype:
        #     msg.append(VehicleName) # Where is VehicleName defined???
        #     msg.append('STS') # Message Type
        # else:
        #     msg.append(SelectedName) # Vehicle Name
        #     msg.append('CMD') # Message Type
