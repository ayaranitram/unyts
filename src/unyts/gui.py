#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 10:38:47 2024

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.3.6'
__release__ = 20240601
__all__ = ['start_gui']

import logging
import tkinter as tk
from tkinter import ttk
from stringthings import get_number, is_numeric
from unyts import __version__ as unyts_version
from .converter import convert
from .dictionaries import _all_units
from .errors import NoConversionFoundError
from .database import save_memory, load_memory, clean_memory, delete_cache, unyts_parameters_ as up_, set_fvf
import pathlib, os
import webbrowser


_all_units_str = _all_units()


class UnytsApp(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.pack()

        ttk.Label(text="Unyts converter", font=(None, 16, 'bold'), padding=5).pack()

        frame = ttk.Frame(padding=5)
        self.frame = frame
        self.frame.pack()

        ttk.Label(frame, text="unit").grid(column=1, row=0, pady=3)
        ttk.Label(frame, text="value").grid(column=2, row=0, pady=3)

        ttk.Label(frame, text="from").grid(column=0, row=1)
        self.from_unit_val = tk.StringVar()
        self.from_unit = ttk.Entry(frame, textvariable=self.from_unit_val)
        self.from_unit.grid(column=1, row=1, pady=3, padx=1)
        self.from_unit.bind('<Key-Return>', self._calculate)
        self.from_value_val = tk.StringVar()
        self.from_value = ttk.Entry(frame, textvariable=self.from_value_val)
        self.from_value.grid(column=2, row=1, pady=3, padx=1)
        self.from_value.bind('<Key-Return>', self._calculate)

        ttk.Label(frame, text="to").grid(column=0, row=2)
        self.to_unit_val = tk.StringVar()
        self.to_unit = ttk.Entry(frame, textvariable=self.to_unit_val)
        self.to_unit.grid(column=1, row=2, pady=3, padx=1)
        self.to_unit.bind('<Key-Return>', self._calculate)
        self.to_value_val = tk.StringVar()
        self.to_value = ttk.Entry(frame, textvariable=self.to_value_val)
        self.to_value.grid(column=2, row=2, pady=3, padx=1)
        self.to_value.bind('<Key-Return>', self._rcalculate)

        self.button_text = tk.StringVar()
        self.button_text.set("convert")
        self.convert_button = ttk.Button(frame, textvariable=self.button_text)
        self.convert_button.grid(columnspan=3, row=3, pady=7)
        self.convert_button.bind('<ButtonRelease>', self._calculate)
        self.frame.bind('<Motion>', lambda x: self.button_text.set("convert"))

    def _validate_from_units(self, *args):
        if self.from_unit_val.get() not in _all_units_str and not is_numeric(self.from_unit_val.get()):
            return False
        else:
            return True

    def _validate_to_units(self, *args):
        if self.to_unit_val.get() not in _all_units_str and not is_numeric(self.to_unit_val.get()):
            return False
        else:
            return True

    def _get_from(self):
        from_value = self.from_value_val.get().strip()
        from_unit = self.from_unit_val.get().strip()
        if len(from_value) == 0 and len(from_unit) > 0 and not is_numeric(from_unit):
            pass  # is OK
        elif len(from_unit) == 0 and len(from_value) > 0 and not is_numeric(from_value):
            from_value, from_unit = from_unit, from_value
        elif is_numeric(from_value) and not is_numeric(from_unit):
            from_value = get_number(from_value)
        elif not is_numeric(from_value) and is_numeric(from_unit):
            from_value, from_unit = get_number(from_unit), from_value
        elif not is_numeric(from_value) and not is_numeric(from_unit):
            self.from_value_val.set(f"wrong number format")
            from_value, from_unit = None, None
        self.from_unit_val.set(from_unit)
        self.from_value_val.set(from_value)
        return from_unit, from_value

    def _get_to(self):
        to_value = self.to_value_val.get().strip()
        to_unit = self.to_unit_val.get().strip()
        if len(to_value) == 0 and len(to_unit) > 0 and not is_numeric(to_unit):
            pass  # is OK
        elif len(to_unit) == 0 and len(to_value) > 0 and not is_numeric(to_value):
            to_value, to_unit = to_unit, to_value
        elif is_numeric(to_value) and not is_numeric(to_unit):
            to_value = get_number(to_value)
        elif not is_numeric(to_value) and is_numeric(to_unit):
            to_value, to_unit = get_number(to_unit), to_value
        elif not is_numeric(to_value) and not is_numeric(to_unit):
            self.to_value_val.set(f"wrong number format")
            to_value, to_unit = None, None
        self.to_unit_val.set(to_unit)
        self.to_value_val.set(to_value)
        return to_unit, to_value

    def _calculate(self, *args):
        self.button_text.set("looking for conversion...")
        from_unit, from_value = self._get_from()
        to_unit, to_value = self._get_to()
        if from_unit is None and from_value is None and to_unit is None and to_value is None:
            self.from_value_val.set("")
            self.from_unit_val.set("")
            self.to_value_val.set("")
            self.to_unit_val.set("")
            self.button_text.set("convert")
            return None
        if from_value == "" and is_numeric(to_value):
            return self._rcalculate()
        try:
            to_value = convert(from_value, from_unit, to_unit,
                               print_conversion_path=up_.print_path_)
            self.to_value_val.set(str(to_value))
        except NoConversionFoundError:
            self.to_value_val.set("")
            self.button_text.set("no conversion found!")
            return None
        self.button_text.set("convert")

    def _rcalculate(self, *args):
        self.button_text.set("looking for conversion...")
        from_unit, from_value = self._get_to()
        to_unit, to_value = self._get_from()
        if from_unit is None and from_value is None and to_unit is None and to_value is None:
            self.from_value_val.set("")
            self.from_unit_val.set("")
            self.to_value_val.set("")
            self.to_unit_val.set("")
            self.button_text.set("convert")
            return None
        if from_value == "" and is_numeric(to_value):
            return self._calculate()
        try:
            to_value = convert(from_value, from_unit, to_unit,
                               print_conversion_path=up_.print_path_)
            self.from_value_val.set(str(to_value))
        except NoConversionFoundError:
            self.from_value_val.set("")
            self.button_text.set("no conversion found!")
            return None
        self.button_text.set("convert")


def start_gui():
    def close_gui():
        logging.info("INFO:shutting down Unyts.")
        if up_.cache_:
            logging.info("saving memory...")
            save_memory()
        root.destroy()
    if up_.memory_:
        load_memory()
    else:
        delete_cache()
    def open_help():
        webbrowser.open('https://github.com/ayaranitram/unyts/blob/master/unyts_demo.ipynb')
    def open_git():
        webbrowser.open('https://github.com/ayaranitram/unyts')

    logging.info("starting Unyts GUI...")
    w, h = 325, 185
    root = tk.Tk(screenName='Unyts')
    root.geometry(f"{w}x{h}")
    root.maxsize(w, h)
    root.minsize(w, h)
    root.resizable(False, False)
    icon_file = 'unyts_icon.ico'
    current_dir = pathlib.Path(__file__).parent.resolve()
    icon_path = os.path.join(current_dir, icon_file)
    root.iconbitmap(icon_path)

    # variables
    _cache_ = tk.BooleanVar()
    _cache_.set(up_.cache_)
    _verbosity_ = tk.BooleanVar()
    _verbosity_.set(up_.verbose_)
    _print_path_ = tk.BooleanVar()
    _print_path_.set(up_.print_path_)

    # setting menu
    root.option_add('*tearOff', False)
    unyts_menu = tk.Menu(root)
    root.config(menu=unyts_menu)
    # File menu
    file_menu = tk.Menu(unyts_menu)
    unyts_menu.add_cascade(label='File', menu=file_menu)
    file_menu.add_command(label='Save memory', command=save_memory)
    file_menu.add_command(label='Reload memory', command=load_memory)
    file_menu.add_command(label='Clean memory', command=clean_memory)
    file_menu.add_command(label='Delete cache', command=delete_cache)
    file_menu.add_separator()
    file_menu.add_command(label='Exit', command=close_gui)
    # Options menu
    options_menu = tk.Menu(unyts_menu)
    unyts_menu.add_cascade(label='Options', menu=options_menu)
    options_menu.add_command(label="Set FVF (in CMD)", command=set_fvf)
    options_menu.add_separator()
    options_menu.add_checkbutton(label='Reload on next start', variable=up_.reload_, command=up_.reload_next_time)
    options_menu.add_checkbutton(label='Show conversion path', variable=_print_path_, command=up_.print_path)
    options_menu.add_checkbutton(label='Verbosity', variable=_verbosity_, command=up_.verbose)
    options_menu.add_checkbutton(label='Cache', variable=_cache_, command=up_.cache)
    # help menu
    help_menu = tk.Menu(unyts_menu)
    unyts_menu.add_cascade(label='Help', menu=help_menu)
    help_menu.add_command(label='Help', command=open_help)
    help_menu.add_command(label='GitHub', command=open_git)
    help_menu.add_command(label=f"Version {unyts_version}")

    unyts_gui = UnytsApp()
    unyts_gui.master.title("Unyts converter")
    root.protocol("WM_DELETE_WINDOW", close_gui)
    unyts_gui.mainloop()
