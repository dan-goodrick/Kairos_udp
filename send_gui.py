import tkinter as tk

strmDict = {"1":"hello", "2":"world"}
message = '#|1.0|VEH_MHAFB1|CMD|123|45|56837|S,0|A,0|B,100|G,1|V,0|X,0,1,0,0,0,,,|Y,0,0,0,0,0,,,|Z,0,0,0,,,,,|C,XXX'

class GUI:
    def __init__(self):
        global strmDict
        self.frequency = 1000
        self.port = 7201
        self.strmDict = strmDict
        self.message = message
        self.window = tk.Tk()
        self.window.title("Message Configuration")
        self.window.geometry('350x200')
        self.sending_enabled = False
        self.button = tk.Button(self.window,text="Start",command=self.clicked)
        self.button.grid(column=0, row=0)
        self.show_IP()
        self.show_params()
        # self.window.after(self.frequency,self.send_message)
        self.window.mainloop()

    def clicked(self):
        if self.sending_enabled: #start->stop (get configuration)
            self.sending_enabled = False
            self.show_IP()
            self.button.configure(text="Start")
        else:                   #stopped->started (send with config)
            self.sending_enabled = True
            self.show_params()
            self.window.after(self.frequency,self.show_params)
            self.button.configure(text="Stop")

    def show_IP(self):
        text="IP Address:"
        self.ip_label = tk.Label(self.window,text=text, width=len(text)+1)
        self.ip_label.grid(column=0, row=1)

        self.ip_field = tk.Entry(self.window,width=15)
        self.ip_field.grid(column=1, row=1)

        text = 'Port:'
        self.port_label = tk.Label(self.window,text=text, width=len(text)+1)
        self.port_label.grid(column=0, row=2)

        self.port_field = tk.Entry(self.window)
        self.port_field.insert(0,self.port)
        self.port_field.grid(column=1, row=2)
        print(self.port_field.get())
        text = 'Message Frequency (ms):'
        self.freq_label = tk.Label(self.window,text=text, width=len(text)+1)
        self.freq_label.grid(column=0, row=3)

        self.freq_field = tk.Entry(self.window,width=5)
        self.freq_field.grid(column=1, row=3)
        self.freq_field.insert(0,self.frequency)
        print(self.freq_field.get())
        if self.freq_field.get().isnumeric():
            print(f"Sending messages at {self.frequency} Hz")
            self.frequency = int(self.freq_field.get())


    def send_message(self):
        if self.sending_enabled:
            print("sending IP")
            self.window.after(self.frequency,self.send_message)


    def show_params(self):
        for i, (key,value) in enumerate(self.strmDict.items()):
            text = f"{key}: {value}"
            label = tk.Label(self.window,text=text, width=len(text)+1)
            label.grid(column=0, row=i+4)
        # self.window.after(1000,self.receive_messages)


    def start_sending(self):
        if not self.sending_enabled:
            self.window.after(self.frequency,self.send_message)
            self.sending_enabled = True

    def stop_sending(self):
        self.sending_enabled = False



if __name__ == "__main__":
    g = GUI()
