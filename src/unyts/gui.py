import tkinter as tk
from tkinter import ttk
from unyts import convert
class UnytsApp(tk.Frame):
    def __init__(self, master=None):
        super.__init__(master)
        self.pack()

        frame = ttk.Frame(root, padding=10)
        frame.grid()

        from_label = ttk.Label(frame, text="from").grid(column=0, row=1)
        self.from_unit = ttk.Entry(frame).grid(column=1, row=1)
        self.from_unit.bind('<Key-Return>', self._calculate)
        self.from_value = ttk.Entry(frame).grid(column=2, row=1)
        self.from_value.bind('<Key-Return>', self._calculate)

        to_label = ttk.Label(frame, text="to").grid(column=0, row=2)
        self.to_unit = ttk.Entry(frame).grid(column=1, row=2)
        self.to_unit.bind('<Key-Return>', self._calculate)
        self.to_value = ttk.Entry(frame).grid(column=2, row=2)
        self.to_value.bind('<Key-Return>', self._rcalculate)
        self.convert_button = ttk.Button(frame, text="convert")
        self.convert_button.grid(column=0, row=3)
        self.convert_button.bind('<ButtonRelease>', self._calculate)

    def _calculate(self):
        to_value = convert(float(self.from_value.get()),
                           self.from_unit.get(),
                           self.to_unit.get(),
                           print_conversion_path=False)


    def _rcalculate(self):
        to_value = convert(float(self.to_value.get()),
                           self.to_unit.get(),
                           self.from_unit.get(),
                           print_conversion_path=False)

def start_gui():
    root = tk.Tk(screenName='Unyts')
    unyts_gui = UnytsApp()
    unyts_gui.master.title("Unyts converter")
    unyts_gui.mainloop()