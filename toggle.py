import tkinter as tk

def toggle():
    if var.get() == "Stop UDP":
        print("turning on...")
    else:
        print("turning off...")

root = tk.Tk()
var = tk.StringVar()
button = tk.Checkbutton(root, onvalue="Stop UDP", offvalue="Start UDP",
                        indicatoron=False,
                        variable=var, #enables var.get
                        textvariable=var, #prints onvalue/offvalue on button
                        # selectcolor="green",
                        command=toggle)


var.set("Start UDP") # initial Button text
button.pack()

root.mainloop()
