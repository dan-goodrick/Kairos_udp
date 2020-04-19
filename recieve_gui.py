import tkinter as tk

sending_enabled = False

def send_message():
    if sending_enabled:

        root.after(500,send_message)

def recieve_messages():
    print("Getting Messages")
    root.after(1000,recieve_messages)


def start_sending():
    global sending_enabled
    if not sending_enabled:
        root.after(500,send_message)
        sending_enabled = True

def stop_sending():
    global sending_enabled
    sending_enabled = False


root = tk.Tk()

startButton = tk.Button(root,text="Start",command=start_sending)
startButton.grid()
stopButton = tk.Button(root,text="Stop",command=stop_sending)
stopButton.grid()

root.after(1000,receive_messages)

root.mainloop()
