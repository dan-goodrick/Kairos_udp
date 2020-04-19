# mandelbrot fractal,  z=z^2+c
import tkinter as tk

class GUI():
    def __init__(self):
        self.root = tk.Tk()
        self.frequency = 500
        self.build_frame()
        # self.root.after(self.frequency, lambda: self.send_message(msg))
        tk.mainloop()

    def build_frame(self):
        self.root.title("Configure Message")
        self.button = tk.Button(self.root,text="Start",command=self.clicked)
        self.button.pack()

    def clicked(self):
        if self.button['text'] == 'Start':
            self.button['text'] = 'Stop'
            self.root.after(0)
        else:
            self.button['text'] = 'Start'
            self.root.after(self.frequency, self.send_message)

    def send_message(self):
        print(f"sending messsages")
        self.root.after(self.frequency, self.send_message)



if __name__ == "__main__":
    window = GUI()
