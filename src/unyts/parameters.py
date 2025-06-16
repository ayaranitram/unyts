#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 18:24:20 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.6.9'
__release__ = 20250615
__all__ = ['unyts_parameters_', 'print_path', 'reload', 'raise_error', 'cache', 'set_density', 'get_density',
           'recursion_limit', 'verbose', 'set_algorithm', 'set_parallel']

import os.path
from json import load as json_load, dump as json_dump
from os.path import isfile, isdir
from pathlib import Path
from sys import getrecursionlimit
from time import time
from .helpers.logger import logger

ini_path = Path(__file__).with_name('parameters.ini').absolute()
ini_backup = Path(__file__).with_name('parameters.backup').absolute()
dir_path = os.path.dirname(ini_path) + '/'
off_switches = ('false', 'off', 'no', 'none', 'null', 'not', '')
__max_recursion_default__ = 12
__max_generations_default__ = 25
__timeout__ = 30
__default_density__ = 0.997
__default_fvf__ = 1.0
__default_logger_level__ = "INFO"

class UnytsParameters(object):
    """
    class to load the user preferences
    """

    def __init__(self, reload=None) -> None:
        self.config_files_folder_ = dir_path
        self.print_path_ = False
        self.cache_ = True
        self.raise_error_ = True
        self.verbose_ = False
        self.verbose_details_ = 0
        self.reduce_parentheses_ = True
        self.show_version_ = True
        self.density_ = __default_density__  # g/cm3
        self.fvf_ = __default_fvf__  # res_vol/std_vol
        self.max_recursion_ = __max_recursion_default__
        self.algorithm_ = 'lean_BFS'
        self.max_generations_ = __max_generations_default__
        self.timeout_ = __timeout__
        self.load_params()
        self.reload_ = self.reload_ if reload is None else bool(reload)
        self.memory_ = not self.reload_
        self.last_path_str = ""
        self.gui = False
        self.threading_ = self.threading_available()
        self.multiprocessing_ = self.multiprocessing_available()
        self.parallel_ = (self.threading_ or self.multiprocessing_) and self.parallel_
        self._deactivate_parallel = True  # to hide the Parallel menu in the GUI
        self._warnings = []
        self._start_time = 0

    def threading_available(self):
        try:
            import threading
            threading_ = True
        except ModuleNotFoundError:
            threading_ = False
        return threading_

    def multiprocessing_available(self):
        try:
            import multiprocessing
            multiprocessing_ = True
        except ModuleNotFoundError:
            multiprocessing_ = False
        return multiprocessing_

    def load_params(self) -> None:
        if isfile(ini_path):
            with open(ini_path, 'r') as f:
                params = json_load(f)
        else:
            params = {'print_path': False,
                      'cache': True,
                      'reload': True,
                      'raise_error': True,
                      'verbose': False,
                      'verbose_details': 0,
                      'reduce_parentheses': True,
                      'show_version': False,
                      'density': __default_density__, # g/cm3
                      'fvf': __default_fvf__,
                      'max_recursion': __max_recursion_default__,
                      'algorithm': 'lean_BFS',
                      'max_generations': __max_generations_default__,
                      'timeout': __timeout__,
                      'parallel': False,
                      'config_files_folder': None}
            with open(ini_path, 'w') as f:
                json_dump(params, f)
        self.print_path_ = params['print_path'] if 'print_path' in params else False
        self.cache_ = params['cache'] if 'cache' in params else True
        self.reload_ = params['reload'] if 'reload' in params else False
        self.raise_error_ = params['raise_error'] if 'raise_error' in params else True
        self.verbose_ = params['verbose'] if 'verbose' in params else False
        self.verbose_details_ = params['verbose_details'] if 'verbose_details' in params else 0
        self.reduce_parentheses_ = params['reduce_parentheses'] if 'reduce_parentheses' in params else True
        self.show_version_ = params['show_version'] if 'show_version' in params else True
        self.density_ = params['density'] if 'density' in params else __default_density__  # g/cm3
        self.fvf_ = params['fvf'] if 'fvf' in params else __default_fvf__
        self.max_recursion_ = params['max_recursion'] if 'max_recursion' in params else __max_recursion_default__
        self.algorithm_ = params['algorithm'] if 'algorithm' in params else 'BFS'
        self.max_generations_ = params['max_generations'] if 'max_generations' in params else __max_generations_default__
        self.timeout_ = params['timeout'] if 'timeout' in params else __timeout__
        self.parallel_ = params['parallel'] if 'parallel' in params else False
        self.config_files_folder_ = dir_path if ('config_files_folder' not in params or params['config_files_folder'] is None) \
            else params['config_files_folder'] if ('config_files_folder' in params and isdir(params['config_files_folder'])) \
            else self.config_files_folder_

        if self.show_version_ and isfile(ini_backup):
            with open(ini_backup, 'r') as f:
                params = json_load(f)
            logger.info("Restoring configuration from previous installation...")
            self.print_path_ = params['print_path'] if 'print_path' in params else False
            self.cache_ = params['cache'] if 'cache' in params else True
            self.raise_error_ = params['raise_error'] if 'raise_error' in params else True
            self.verbose_ = params['verbose'] if 'verbose' in params else False
            self.verbose_details_ = params['verbose_details'] if 'verbose_details' in params else 0
            self.reduce_parentheses_ = params['reduce_parentheses'] if 'reduce_parentheses' in params else True
            self.density_ = params['density'] if 'density' in params else __default_density__  # g/cm3
            self.fvf_ = params['fvf'] if 'fvf' in params else __default_fvf__
            self.max_recursion_ = params['max_recursion'] if 'max_recursion' in params else __max_recursion_default__
            self.algorithm_ = params['algorithm'] if 'algorithm' in params else 'BFS'
            self.max_generations_ = params['max_generations'] if 'max_generations' in params else __max_generations_default__
            self.timeout_ = params['timeout'] if 'timeout' in params else __timeout__
            self.parallel_ = params['parallel'] if 'parallel' in params else True
            self.config_files_folder_ = dir_path if ('config_files_folder' not in params or params['config_files_folder'] is None) \
                else params['config_files_folder'] if ('config_files_folder' in params and isdir(params['config_files_folder'])) \
                else self.config_files_folder_

    def save_params(self) -> None:
        params = {'print_path': self.print_path_,
                  'cache': self.cache_,
                  'reload': self.reload_,
                  'raise_error': self.raise_error_,
                  'verbose': self.verbose_,
                  'verbose_details': self.verbose_details_,
                  'reduce_parentheses': self.reduce_parentheses_,
                  'show_version': self.show_version_,
                  'density': self.density_,
                  'fvf': self.fvf_,
                  'max_recursion': self.max_recursion_,
                  'algorithm': self.algorithm_,
                  'max_generations': self.max_generations_,
                  'timeout': self.timeout_,
                  'parallel': self.parallel_,
                  'config_files_folder': self.config_files_folder_ if self.config_files_folder_ != dir_path else None,
                  'logger_level': logger.get_current_level()}
        with open(ini_path, 'w') as f:
            json_dump(params, f)
        with open(ini_backup, 'w') as f:
            json_dump(params, f)

    def print_path(self, switch=None) -> None:
        _prev = self.print_path_
        if switch is None:
            self.print_path_ = not self.print_path_
        elif type(switch) is str:
            if switch.lower().strip() in off_switches:
                self.print_path_ = False
            else:
                self.print_path_ = True
        else:
            self.print_path_ = bool(switch)
        if _prev != self.print_path_:
            logger.info(f"print path {'ON' if self.print_path_ else 'OFF'}")
        self.save_params()

    def cache(self, switch=None) -> None:
        if switch is None:
            self.cache_ = not self.cache_
        elif type(switch) is str:
            if switch.lower().strip() in off_switches:
                self.cache_ = False
            else:
                self.cache_ = True
        else:
            self.cache_ = bool(switch)
        logger.info(f"cache {'ON' if self.cache_ else 'OFF'}")
        self.save_params()

    def raise_error(self, switch=None) -> None:
        if switch is None:
            self.raise_error_ = not self.raise_error_
        elif type(switch) is str:
            if switch.lower().strip() in off_switches:
                self.raise_error_ = False
            else:
                self.raise_error_ = True
        else:
            self.raise_error_ = bool(switch)
        logger.info(f"raise_error {'ON' if self.raise_error_ else 'OFF'}")
        self.save_params()

    def verbose(self, switch=None) -> None:
        _prev = self.verbose_
        if type(switch) is int:
            self.verbose_details_ = switch
            if switch <= 0:
                switch = False
            else:  # switch >= 1:
                switch = True
        if switch is None:
            self.verbose_ = not self.verbose_
        elif type(switch) is str:
            if switch.lower().strip() in off_switches:
                self.verbose_ = False
            else:
                self.verbose_ = True
        else:
            self.verbose_ = bool(switch)
        if _prev != self.verbose_:
            logger.info(f"verbose {'ON' if self.verbose_ else 'OFF'}")
        self.save_params()

    def set_logger_level(self, level:str="INFO") -> None:
        if type(level) is str and level.upper() in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            logger.set_level(level)
            self.save_params()

    def reload_next_time(self, switch=None):
        if switch is None:
            self.reload_ = not self.reload_
        elif type(switch) is str:
            if switch.lower().strip() in off_switches:
                self.reload_ = False
            else:
                self.reload_ = True
        else:
            self.reload_ = bool(switch)
        if self.reload_:
            logger.info("Unyts will recreate dictionaries next time.")
        else:
            logger.info("Unyts will try to load dictionaries from cache next time.")
        self.save_params()

    def recursion_limit(self, limit=None):
        if limit is None:
            return self.max_recursion_
        elif (type(limit) is str and limit.lower() == 'max') or limit is False:
            self.max_recursion_ = getrecursionlimit() - 15
        elif limit is True:
            self.max_recursion_ = __max_recursion_default__
        elif type(limit) is int:
            self.max_recursion_ = min(limit, getrecursionlimit() - 15)
        else:
            raise ValueError(f"not valid recursion limit, must be an integer or boolean.")
        self.save_params()
        return self.max_recursion_

    def generations_limit(self, limit=None):
        if limit is None:
            return self.max_generations_
        elif (type(limit) is str and limit.lower() == 'max') or limit is False:
            self.max_generations_ = __max_generations_default__
        elif limit is True:
            self.max_generations_ = __max_generations_default__
        elif type(limit) is int:
            self.max_generations_ = limit
        else:
            raise ValueError(f"not valid generations limit, must be an integer or boolean.")
        self.save_params()
        return self.max_generations_

    def get_algorithm(self):
        return self.algorithm_

    def set_algorithm(self, algorithm:str):
        if algorithm not in ['BFS', 'lean_BFS', 'DFS', 'hybrid_BFS']:
            logger.error(f"Valid algorithms are 'BFS', 'lean_BFS', 'hybrid_BFS', and 'DFS' not '{algorithm}'.")
        elif algorithm == 'hybrid_BFS' and not self.threading_:
            logger.critical("threading module not available in this Python installation.")
            if self.get_algorithm() == 'hybrid_BFS':
                _ = set_algorithm('lean_BFS')
            else:
                logger.info(f"keeping {self.get_algorithm()} as search algorithm.")
        else:
            self.algorithm_ = algorithm
            if self.verbose_:
                logger.info(f"{algorithm} set as search algorithm.")
            msg = "The search memory must be cleansed if intended to repeat searches with a different algorithm."
            if msg not in self._warnings:
                logger.warning(msg)
                self._warnings.append(msg)
            self.save_params()

    def get_algorithm(self):
        return self.algorithm_

    def set_parallel(self, method:str):
        if method is None:
            self.parallel_ = True
            self.threading_ = self.threading_available()
            self.multiprocessing_ = self.multiprocessing_available()
        elif type(method) is bool:
            self.parallel_ = method
            self.threading_ = self.threading_available()
            self.multiprocessing_ = self.multiprocessing_available()
        elif type(method) is str and len(method.strip()) > 0:
            if method.lower().strip()[0] == 't':
                self.parallel_ = True
                self.threading_ = True
                self.multiprocessing_ = False
            elif method.lower().strip()[0] in 'mp':
                self.parallel_ = True
                self.threading_ = False
                self.multiprocessing_ = True
            else:
                self.parallel_ = False
                self.threading_ = self.threading_available()
                self.multiprocessing_ = self.multiprocessing_available()
        else:
            raise ValueError(f"method argument should be set to 'threading' of 'multiprocessing', False to deactivate, or None for automatic detection.")
        msg = f"Parallel processing {'activated' if self.parallel_ else 'deactivated'}{', using ' if self.parallel_ else ''}{('multiprocessing' if self.multiprocessing_ else 'threading' if self.threading_ else '') if self.parallel_ else ''}."
        logger.info(msg)

    def get_parallel(self):
        return self.parallel_

    def set_timeout(self, timeout:int=120):
        if type(timeout) is not int:
            raise TypeError("´timeout´ must be entered in seconds, as integer")
        self.timeout_ = timeout
        if timeout > 0:
            logger.info(f"path searches limited to {timeout} seconds.")
        else:
            logger.warning(f"path searches may run for unlimited time.")
        self.save_params()

    def get_timeout(self):
        return self.timeout_

    def is_intime(self):
        if self._start_time == 0:
            self._start_time = time()
            return True
        elif time() - self._start_time <= self.timeout_:
            return True
        else:
            return False

    def reset_start_time(self):
        self._start_time = 0

    def set_user_folder(self, path=None):
        if path is None:
            self.config_files_folder_ = dir_path
        elif isdir(path):
            self.config_files_folder_ = path + '' if not path.endswith('/') and not path.endswith('\\') else '/'
        else:
            logger.warning(f"Folder {path} doesn't exists, user folder not changed.")

    def get_user_folder(self):
        return self.config_files_folder_


unyts_parameters_ = UnytsParameters()


def print_path(switch=None) -> None:
    unyts_parameters_.print_path(switch)


def raise_error(switch=None) -> None:
    unyts_parameters_.raise_error(switch)


def verbose(switch=None) -> None:
    unyts_parameters_.verbose(switch)


def cache(switch=None) -> None:
    unyts_parameters_.cache(switch)

def recursion_limit(limit=None) -> int:
    return unyts_parameters_.recursion_limit(limit)


def set_density(density: float = None, units: str = 'g/cm3') -> None:
    from .units.ratios import Density
    if density is None:
        print('Please enter density g/cm³ or enter a tuple density, units like: 997, kg/m³ :')
        while density is None:
            density = input(' density (g/cm³) = ')
            if ',' in density and len(density.split(',')) == 2:
                density, units = density.strip('()').split(',')
                density, units = float(density), units.strip(' ()')
            elif ',' not in density:
                try:
                    density = float(density)
                except:
                    density = None
            else:
                density = None
    if not isinstance(density, (int, float)) and not type(density) is Density:
        raise ValueError("'density' must be a float or int.")
    elif type(density) is Density:
        density = density.to('g/cm3')
        density, units = density.value, density.unit
    if units.lower() not in ('g/cc', 'g/cm3', 'g/cm³'):
        from .converter import convert
        from .errors import NoConversionFoundError
        try:
            density = convert(density, units, 'g/cm3')
        except NoConversionFoundError:
            raise ValueError("density 'units' are not valid.")
        if density is None:
            raise ValueError("density 'units' are not valid.")
    unyts_parameters_.density_ = density
    logger.info(f"density set to {density} g/cm³")
    unyts_parameters_.save_params()


def _get_density() -> float:
    while unyts_parameters_.density_ is None:
        density = input("Please set density value: ")
        try:
            density = float(density)
            unyts_parameters_.density_ = density
        except ValueError:
            print("'density' must be float or int.")
            density = None
    return unyts_parameters_.density_


def get_density():
    from .units.ratios import Density
    if unyts_parameters_.density_ is None:
        raise ValueError("'density' is not set.")
    return Density(unyts_parameters_.density_, 'g/cc')


def reload() -> None:
    unyts_parameters_.reload_ = True
    unyts_parameters_.save_params()
    logger.info("On next 'import unyts', the dictionary and network will be re-created.\n It might be required to restart the Python kernel.")


def set_algorithm(algorithm:str):
    if algorithm not in ['BFS', 'lean_BFS', 'DFS', 'hybrid_BFS']:
        raise ValueError(f"valid algorithms are 'BFS', 'lean_BFS', 'hybrid_BFS', and 'DFS' not {algorithm}.")
    unyts_parameters_.set_algorithm(algorithm)


def get_algorithm():
    return unyts_parameters_.algorithm_


def set_parallel(method:str):
    unyts_parameters_.set_parallel(method)


def get_parallel():
    return unyts_parameters_.get_parallel()


def set_timeout(timeout:int=None):
    if timeout is None:
        timeout = __timeout__
    if timeout is False:
        timeout = -1
    elif timeout is True:
        timeout = __timeout__
    if type(timeout) is not int:
        raise TypeError("´timeout´ must be entered in seconds, as integer")
    return unyts_parameters_.set_timeout(timeout)


def get_timeout():
    return unyts_parameters_.get_timeout()


def set_logging_level(level:str="WARNING"):
    unyts_parameters_.set_logger_level(level)

