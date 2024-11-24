#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 10:38:47 2024

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.5'
__release__ = 20241123
__all__ = ['start_gui']

import logging
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from time import process_time
from tkinter import ttk
from stringthings import get_number, is_numeric
from unyts import __version__ as unyts_version
from .converter import convert
from .dictionaries import _all_units
from .errors import NoConversionFoundError, NoFVFError
from .database import save_memory, load_memory, clean_memory, delete_cache, units_network  # set_fvf
from .parameters import unyts_parameters_  # set_density
import pathlib, os
import webbrowser


class UnytsApp(tk.Frame):
    _all_units_str = _all_units()

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

        self.result_str = tk.StringVar()
        self.result_str.set("")
        self.result_msg = ttk.Label(frame, textvariable=self.result_str)
        self.result_msg.config(foreground='#5f5f5f')
        self.result_msg.grid(column=0, columnspan=3, row=4)

        # conversion path marquee
        self._first_char = tk.IntVar()
        self._first_char.set(0)
        self._msg_len = tk.IntVar()
        self._msg_len.set(len(unyts_parameters_.last_path_str))
        self._msg_dir = tk.BooleanVar()
        self._msg_dir.set(True)
        self._max_len = 53
        self._path_marquee = None

        path_frame = ttk.Frame(padding=0)
        self.path = path_frame
        if unyts_parameters_.print_path_:
            self.path.pack()
        self.path_str = tk.StringVar()
        self.path_str.set("")
        self.path_msg = ttk.Label(path_frame, textvariable=self.path_str)
        self.path_msg.grid(column=0, row=0)

        # # user input row
        # user_input = ttk.Frame(padding=0)
        # self.input = user_input
        # self.input_label_str = tk.StringVar()
        # self.input_label = ttk.Label(textvariable=self.input_label_str)
        # # self.input_label.grid(column=0, row=0)
        # self.input_value_str = tk.StringVar()
        # self.input_value = ttk.Entry(user_input, textvariable=self.input_value_str)
        # # self.input_value.grid(column=1, row=0)
        # self.input_button = ttk.Button(user_input, text='set')
        # # self.input_button.grid(columnspan=3, row=0)
        # self.input_button.bind('<ButtonRelease>', self._get_input)

    def _validate_from_units(self, *args):
        if self.from_unit_val.get() not in UnytsApp._all_units_str and not is_numeric(self.from_unit_val.get()):
            return False
        else:
            return True

    def _validate_to_units(self, *args):
        if self.to_unit_val.get() not in UnytsApp._all_units_str and not is_numeric(self.to_unit_val.get()):
            return False
        else:
            return True

    def _get_from(self):
        from_value = self.from_value_val.get().strip().replace("no conversion found!", "").replace("wrong number format", "")
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
            self.from_value_val.set("wrong number format")
            from_value, from_unit = None, None
        self.from_unit_val.set(from_unit)
        self.from_value_val.set(from_value)
        return from_unit, from_value

    def _get_to(self):
        to_value = self.to_value_val.get().strip().replace("no conversion found!", "").replace("wrong number format", "")
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
            self.to_value_val.set("wrong number format")
            to_value, to_unit = None, None
        self.to_unit_val.set(to_unit)
        self.to_value_val.set(to_value)
        return to_unit, to_value

    def _calculate(self, *args):
        self._display_path(" ")
        start_time = process_time()
        from_unit, from_value = self._get_from()
        to_unit, to_value = self._get_to()
        if from_unit is None and from_value is None and to_unit is None and to_value is None:
            self.from_value_val.set("")
            self.from_unit_val.set("")
            self.to_value_val.set("")
            self.to_unit_val.set("")
            self.button_text.set("convert")
            return
        if from_value == "" and is_numeric(to_value):
            return self._rcalculate()
        self.to_value_val.set("")
        try:
            to_value = convert(from_value, from_unit, to_unit,
                               print_conversion_path=unyts_parameters_.print_path_)
            self.to_value_val.set(str(to_value))
            end_time = process_time()
            self._calculation_time(start_time, end_time)
            self._display_path()
        except NoConversionFoundError:
            end_time = process_time()
            self._calculation_time(start_time, end_time)
            self._display_path("no conversion found!")
            return
        except NoFVFError:
            end_time = process_time()
            self._calculation_time(start_time, end_time)
            self._display_path(error="Please set FVF constant from Options menu.")
            return
        except:
            end_time = process_time()
            self._calculation_time(start_time, end_time)
            self._display_path(error="Unknown error.")
            return

    def _rcalculate(self, *args):
        self._display_path(" ")
        start_time = process_time()
        from_unit, from_value = self._get_to()
        to_unit, to_value = self._get_from()
        if from_unit is None and from_value is None and to_unit is None and to_value is None:
            self.from_value_val.set("")
            self.from_unit_val.set("")
            self.to_value_val.set("")
            self.to_unit_val.set("")
            self.button_text.set("convert")
            return
        if from_value == "" and is_numeric(to_value):
            return self._calculate()
        self.from_value_val.set("")
        try:
            to_value = convert(from_value, from_unit, to_unit,
                               print_conversion_path=unyts_parameters_.print_path_)
            self.from_value_val.set(str(to_value))
            end_time = process_time()
            self._calculation_time(start_time, end_time)
            self._display_path()
        except NoConversionFoundError:
            end_time = process_time()
            self._calculation_time(start_time, end_time)
            self._display_path("no conversion found!")
            return
        except NoFVFError:
            end_time = process_time()
            self._calculation_time(start_time, end_time)
            self._display_path(error="Please set FVF constant from Options menu.")
            return
        except:
            end_time = process_time()
            self._calculation_time(start_time, end_time)
            self._display_path(error="Unknown error.")
            return

    def _calculation_time(self, start_time, end_time):
        total_time = end_time - start_time
        if total_time < 1:
            total_time = round(total_time * 1000, 0)
            time_units = 'milliseconds'
        elif total_time > 60:  # 1 minute
            minutes = total_time // 60
            seconds = round(total_time - minutes, 0)
            total_time = f"{minutes}:{seconds}"
            time_units = 'minutes:seconds'
        elif total_time > 3600:  # 1 hour
            hours = total_time // 3600
            minutes = round((total_time - hours) / 60, 0)
            total_time = f"{hours}:{minutes}"
            time_units = 'hours:minutes'
        else:
            total_time = round(total_time, 2)
            time_units = 'seconds'
        total_time = f"{total_time} {time_units}"
        self.result_str.set(total_time)

    def _partial_msg(self):
        if len(unyts_parameters_.last_path_str) < self._max_len:
            self.path.after_cancel(self._path_marquee)
            self.path_str.set(unyts_parameters_.last_path_str)
            return
        _last_char = self._first_char.get() + self._max_len
        speed = 100
        msg = unyts_parameters_.last_path_str[self._first_char.get(): _last_char]
        self.path_str.set(msg)
        if self._msg_dir.get():
            if _last_char < self._msg_len.get():
                self._first_char.set(self._first_char.get() + 1)
            else:
                self._msg_dir.set(False)
                speed = 2000
        else:
            if self._first_char.get() > 0:
                self._first_char.set(self._first_char.get() - 1)
            else:
                self._msg_dir.set(True)
                speed = 2000
        self._path_marquee = self.path.after(speed, self._partial_msg)

    def _display_path(self, error:str=""):
        if bool(error):
            if self._path_marquee is not None:
                self.path.after_cancel(self._path_marquee)
            self.path_str.set(error)
            self.path_msg.config(foreground='red')
            return
        self.path_msg.config(foreground='#3d3d3d')
        if unyts_parameters_.last_path_str != "" and unyts_parameters_.print_path_:
            if len(unyts_parameters_.last_path_str) < self._max_len:
                self.path_str.set(unyts_parameters_.last_path_str)
            else:
                self._msg_len.set(len(unyts_parameters_.last_path_str))
                self.path_str.set(unyts_parameters_.last_path_str[:self._max_len])
                self._path_marquee = self.path.after(2000, self._partial_msg)
        else:
            self.path_str.set("")

    def _get_input(self):
        self.input_value_str = self.input_value.get().strip()


def start_gui():
    unyts_parameters_.gui = True
    def close_gui():
        logging.info("INFO:shutting down Unyts.")
        if unyts_parameters_.cache_:
            logging.info("saving memory...")
            save_memory()
        root.destroy()
    if unyts_parameters_.memory_:
        load_memory()
    else:
        delete_cache()
    def open_help():
        webbrowser.open('https://github.com/ayaranitram/unyts/blob/master/unyts_demo.ipynb')
    def open_git():
        webbrowser.open('https://github.com/ayaranitram/unyts')
    def print_path():
        unyts_parameters_.print_path()
        if unyts_parameters_.print_path_:
            unyts_gui.path.pack()
            unyts_gui._display_path()
        else:
            unyts_gui._display_path(" ")
            unyts_gui.path.pack_forget()
    def _set_bfs():
        unyts_parameters_.set_algorithm('BFS')
        _bfs_.set(True)
        _lean_bfs_.set(False)
        _dfs_.set(False)
        _hybrid_BFS_.set(False)
    def _set_lean_bfs():
        if unyts_parameters_.get_algorithm() != 'lean_BFS':
            unyts_gui.repeat_search.select()
        unyts_parameters_.set_algorithm('lean_BFS')
        _bfs_.set(False)
        _lean_bfs_.set(True)
        _dfs_.set(False)
        _hybrid_BFS_.set(False)
    def _set_dfs():
        if unyts_parameters_.get_algorithm() != 'DFS':
            unyts_gui.repeat_search.select()
        unyts_parameters_.set_algorithm('DFS')
        _bfs_.set(False)
        _lean_bfs_.set(False)
        _dfs_.set(True)
        _hybrid_BFS_.set(False)
    def _set_hybrid_BFS():
        if unyts_parameters_.get_algorithm() != 'hybrid_BFS':
            unyts_gui.repeat_search.select()
        unyts_parameters_.set_algorithm('hybrid_BFS')
        _bfs_.set(False)
        _lean_bfs_.set(False)
        _dfs_.set(False)
        _hybrid_BFS_.set(True)
    def _set_par_th():
        unyts_parameters_.set_parallel('t')
        _par_th_.set(True)
        _par_mp_.set(False)
        _par_off_.set(False)
        _par_auto_.set(False)
    def _set_par_mp():
        unyts_parameters_.set_parallel('p')
        _par_th_.set(False)
        _par_mp_.set(True)
        _par_off_.set(False)
        _par_auto_.set(False)
    def _set_par_off():
        unyts_parameters_.set_parallel(False)
        _par_th_.set(False)
        _par_mp_.set(False)
        _par_off_.set(True)
        _par_auto_.set(False)
    def _set_par_auto():
        unyts_parameters_.set_parallel(None)
        _par_th_.set(unyts_parameters_.threading_)
        _par_mp_.set(unyts_parameters_.multiprocessing_)
        _par_off_.set(not unyts_parameters_.threading_ and not unyts_parameters_.multiprocessing_)
        _par_auto_.set(True)

    def _set_fvf():
        if unyts_parameters_.fvf_ is not None:
            current_value = f"{unyts_parameters_.fvf_} vol/vol"
            prev_fvf_ = unyts_parameters_.fvf_
        else:
            current_value = None
            prev_fvf_ = None
        fvf = None
        while fvf is None:
            user_input = simpledialog.askstring("formation volume factor",
                                     "Enter FVF in vol/vol or type the value followed by the units, like 1.5 rb/MMscf",
                                                initialvalue=current_value)
            if user_input is None or len(user_input) == 0:
                fvf = False
            elif len(user_input.split()) == 1:
                try:
                    user_input = get_number(user_input)
                    if user_input > 0:
                        fvf = user_input
                except:
                    pass
            elif len(user_input.split()) == 2:
                user_input, unit = user_input.split()
                if unit.lower() == 'vol/vol':
                    unit = 'sm3/sm3'
                try:
                    user_input = get_number(user_input)
                    if user_input > 0:
                        try:
                            units_network.set_fvf(1)
                            unyts_parameters_.fvf_ = 1
                            fvf = convert(user_input, unit, 'sm3/sm3')
                        except NoConversionFoundError:
                            unyts_gui._display_path(error="FVF units {unit} are not valid.")
                            units_network.set_fvf(prev_fvf_)
                            unyts_parameters_.fvf_ = prev_fvf_
                except:
                    pass
        units_network.set_fvf(fvf)
        unyts_parameters_.fvf_ = fvf
        unyts_parameters_.save_params()
        if user_input == fvf:
            unyts_parameters_.last_path_str = f"FVF set as {fvf} vol/vol."
        else:
            unyts_parameters_.last_path_str = f"FVF {user_input} {unit} converted to {fvf} vol/vol"
        unyts_gui._display_path()
    def _set_density():
        if unyts_parameters_.density_ is not None:
            current_value = f"{unyts_parameters_.density_} g/cm³"
        else:
            current_value = None
        density = None
        while density is None:
            user_input = simpledialog.askstring("constant density to convert between volume and mass",
                                     "Enter density in g/cm³ or type the value followed by the units, like: 997 kg/m³",
                                                initialvalue=current_value)
            print(user_input)
            if user_input is None or len(user_input) == 0:
                density = False
            elif len(user_input.split()) == 1:
                try:
                    user_input = get_number(user_input)
                    if user_input > 0:
                        density = user_input
                except:
                    pass
            elif len(user_input.split()) == 2:
                user_input, unit = user_input.split()
                try:
                    user_input = get_number(user_input)
                    if user_input > 0:
                        try:
                            density = convert(user_input, unit, 'g/cm3')
                        except NoConversionFoundError:
                            unyts_gui._display_path(error=f"density units {unit} are not valid.")
                except:
                    pass
        unyts_parameters_.density_ = density
        unyts_parameters_.save_params()
        if user_input == density:
            unyts_parameters_.last_path_str = f"density set as {density} g/cm³."
        else:
            unyts_parameters_.last_path_str = f"density {user_input} {unit} converted to {density} g/cm³"
        unyts_gui._display_path()

    def export_memory():
        cache_path = filedialog.asksaveasfilename(
            title='Save',
            filetypes=(('Cache files', '*.cache'),('All Files', '*.*')),
            initialfile='unyts_memory.cache'
        )
        if cache_path:
            try:
                save_memory(cache_path)
            except:
                logging.error(f"Failed to save memory to file {cache_path}")
        else:
            pass
    def load_memory_file():
        cache_path = filedialog.askopenfilename(
            title='Load',
            filetypes=(('Cache files', '*.cache'),('All Files', '*.*')))
        if cache_path:
            if os.path.isfile(cache_path):
                try:
                    load_memory(cache_path)
                    unyts_gui._display_path()
                except:
                    msg = f"Not able to load memory from file {cache_path}"
                    logging.error(msg)
                    unyts_gui._display_path(error=msg)
            else:
                msg = f"The file {cache_path} doesn't exists."
                logging.error(msg)
                unyts_gui._display_path(error=msg)
        else:
            pass

    def set_cache_folder():
        cache_path = unyts_parameters_.get_user_folder()
        cache_path = filedialog.askdirectory(initialdir=cache_path, title='Cache Folder')
        if cache_path:
            if os.path.isdir(cache_path):
                unyts_parameters_.set_user_folder(cache_path)
            else:
                msg = f"The file {cache_path} doesn't exists."
                logging.error(msg)
                unyts_gui._display_path(error=msg)
        else:
            pass

    logging.info("starting Unyts GUI...")
    w, h = 325, 215
    root = tk.Tk(screenName='Unyts')
    root.geometry(f"{w}x{h}")
    root.maxsize(w, h)
    root.minsize(w, h)
    root.resizable(False, False)
    icon_file = 'unyts_icon.ico'
    current_dir = pathlib.Path(__file__).parent.resolve()
    icon_path = os.path.join(current_dir, icon_file)
    root.iconbitmap(default=icon_path)

    # variables
    _cache_ = tk.BooleanVar()
    _cache_.set(unyts_parameters_.cache_)
    _verbosity_ = tk.BooleanVar()
    _verbosity_.set(unyts_parameters_.verbose_)
    _print_path_ = tk.BooleanVar()
    _print_path_.set(unyts_parameters_.print_path_)
    _bfs_, _lean_bfs_, _dfs_, _hybrid_BFS_ = tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar()
    _bfs_.set(unyts_parameters_.algorithm_ == 'BFS')
    _lean_bfs_.set(unyts_parameters_.algorithm_ == 'lean_BFS')
    _dfs_.set(unyts_parameters_.algorithm_ == 'DFS')
    _hybrid_BFS_.set(unyts_parameters_.algorithm_ == 'hybrid_BFS')
    _par_th_, _par_mp_, _par_off_, _par_auto_ = tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar()
    _par_th_.set(unyts_parameters_.parallel_ and unyts_parameters_.threading_ and not unyts_parameters_.multiprocessing_)
    _par_mp_.set(unyts_parameters_.parallel_ and unyts_parameters_.multiprocessing_)
    _par_off_.set(not unyts_parameters_.parallel_)
    _par_auto_.set(unyts_parameters_.parallel_)

    # setting menu
    root.option_add('*tearOff', False)
    unyts_menu = tk.Menu(root)
    root.config(menu=unyts_menu)
    # File menu
    file_menu = tk.Menu(unyts_menu)
    unyts_menu.add_cascade(label='File', menu=file_menu)
    # File menu > Memory menu
    memory_menu = tk.Menu(unyts_menu)
    memory_menu.add_command(label='Save memory', command=save_memory)
    memory_menu.add_command(label='Clean memory', command=clean_memory)
    memory_menu.add_command(label='Reload memory', command=load_memory)
    memory_menu.add_command(label='Export memory', command=export_memory)
    memory_menu.add_command(label='Import memory', command=load_memory_file)
    file_menu.add_cascade(label='Conversions memory', menu=memory_menu)
    file_menu.add_command(label='Delete cache files', command=delete_cache)
    file_menu.add_separator()
    file_menu.add_command(label='Exit', command=close_gui)
    # Options menu
    options_menu = tk.Menu(unyts_menu)
    unyts_menu.add_cascade(label='Options', menu=options_menu)
    # options_menu.add_command(label="Set FVF (in CMD)", command=set_fvf)
    options_menu.add_command(label="Set FVF", command=_set_fvf)
    options_menu.add_command(label="Set density", command=_set_density)
    #options_menu.add_command(label="Set density (in CMD)", command=set_density)
    options_menu.add_separator()
    options_menu.add_checkbutton(label='Rebuild on next start', variable=unyts_parameters_.reload_,
                                 command=unyts_parameters_.reload_next_time)
    options_menu.add_checkbutton(label='Show conversion path', variable=_print_path_, command=print_path)
    options_menu.add_checkbutton(label='Verbose', variable=_verbosity_, command=unyts_parameters_.verbose)
    options_menu.add_checkbutton(label='Use cache', variable=_cache_, command=unyts_parameters_.cache)
    options_menu.add_separator()
    options_menu.add_command(label='Set cache folder', command=set_cache_folder)
    # Search algorith menu
    search_menu = tk.Menu(unyts_menu)
    search_menu.add_checkbutton(label='BFS', variable=_bfs_, command=_set_bfs)
    search_menu.add_checkbutton(label='lean BFS', variable=_lean_bfs_, command=_set_lean_bfs)
    search_menu.add_checkbutton(label='hybrid BFS', variable=_hybrid_BFS_, command=_set_hybrid_BFS)
    search_menu.add_checkbutton(label='DFS', variable=_dfs_, command=_set_dfs)
    options_menu.add_cascade(label='Search algorithm', menu=search_menu)
    # Parallel menu
    if unyts_parameters_.threading_ or unyts_parameters_.multiprocessing or unyts_parameters_.parallel_:
        parallel_menu = tk.Menu(unyts_menu)
        parallel_menu.add_checkbutton(label='threading', variable=_par_th_, command=_set_par_th)
        if unyts_parameters_.multiprocessing_:
            parallel_menu.add_checkbutton(label='multiprocessing', variable=_par_mp_, command=_set_par_mp)
        parallel_menu.add_checkbutton(label='off', variable=_par_off_, command=_set_par_off)
        parallel_menu.add_checkbutton(label='auto', variable=_par_auto_, command=_set_par_auto)
        options_menu.add_cascade(label='Parallel', menu=parallel_menu)
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
