# -*- coding: utf-8 -*-
"""
Created on Sun May 23 11:18:15 2021

@author: Martín Araya <martinaraya@gmail.com>

helper functions for units modules
"""

def isnumber(string):
    """
    Checks if a string represents a number.
    Valid numbers are:
        positive integers, as in .isnumeric() and .isdigit() methods from string class
        floats, numbers with pointsç
        negative numbers, with dash at the left of the digits
        complex numbers,

    Parameters
    ----------
    string : str
        the string to check if represents a numbers

    Returns
    -------
    True or False

    """
    try:
        complex(string)
        return True
    except:
        return False

def tonumber(string, decimalsign='auto', thousandseparator='auto', parethesismeansnegative=True):
    """
    Cast a string the appropiate numeric type.
    Valid numbers are:
        integers
        real numbers
        complex numbers

    By default, automatically converts comma ',' to period '.' and remove thousand separators

    Parameters
    ----------
    string : str
        the string to convert to number
    decimalsign : str
        The string used as decimal symbol.
    thousandseparator : str
        The string used as thousands separator.

    Returns
    -------
    None.

    """
    def caster(string):
        """
        Helper function to try to cast the string to number

        Parameters
        ----------
        string : str

        Raises
        ------
        ValueError
            if not possible to cast to int, to float or to complex

        Returns
        -------
        value : int, float or complex
            the casted number

        """
        try:
            value = int(string)
        except ValueError:
            try:
                value = float(string)
            except ValueError:
                try:
                    value = complex(string)
                except ValueError:
                    raise ValueError('could not convert string to number: ' + string)
        return value

    def cleaner(string):
        """
        Helper function to clean the string before attemting to cast

        Parameters
        ----------
        string : str

        Returns
        -------
            string : the cleaned string

        """
        def validate(string,ds,ts):
            """
            Helper function to validate the string format

            Parameters
            ----------
            string : str
                the string to validate.
            ds : str
                the expected decimal sign.
            ts : str
                the expected thousand separator.

            Raises
            ------
            ValueError
                if string format is not valid.

            Returns
            -------
            True
                if string format is valid.

            """
            def check(string):
                """
                count the number of decimal signs and thousand separators
                """
                if len(string.split(ds)) > 2 :
                    raise ValueError('the string format is incorrect: ' + string)
                if ts is not None:
                    for part in string.split(ds)[0].split(ts)[1:]:
                        if len(part) != 3:
                            raise ValueError('the string format is incorrect: ' + string)
                if 'e' in string:
                    if 'j' in string:
                        if string.count('j') > 1 or string[-1] != 'j':
                            raise ValueError('the string format is incorrect: ' + string)
                        if not string.split('e')[-1][:-1].isdigit():
                            raise ValueError('the string format is incorrect: ' + string)

                    elif not string.split('e')[-1].isdigit():
                        raise ValueError('the string format is incorrect: ' + string)
                return True

            if 'j' in string:
                for s in ('+','-'):
                    if s in string.strip('+-'):
                        return check(string.strip('+-').split(s)[0]) and check(string.strip('+-').split(s)[1])
            else:
                return check(string)

        string = string.strip().lower()
        newstring = string

        # check parenthesis means negative
        if parethesismeansnegative:
            if '(' in newstring:
                if ')' not in newstring:
                    raise ValueError('the string format is incorrect: ' + string)
                elif 'j' in newstring:
                    pass
                else:
                    if newstring.count('(') == 1 and newstring.count(')') == 1:
                        if newstring[0] == '(' and newstring[-1] == ')':
                            if '-' not in newstring:
                                newstring = '-' + newstring.replace('(','').replace(')','')
                            else:
                                raise ValueError('the string format is incorrect: ' + string)
            elif ')' in newstring:
                raise ValueError('the string format is incorrect: ' + string)
            else:
                pass


        # check thousands separator
        if thousandseparator in ('auto','.') and decimalsign in ('auto',','):
            if ',' in newstring and '.' in newstring:
                if validate(string,ds=',',ts='.'):
                    newstring = newstring.replace('.','').replace(',','.')
                return newstring

        if thousandseparator.strip() == 'auto':
            for ts in ("'","`","´"," ",None):
                if ts is not None and ts in string:
                    newstring = newstring.replace(ts,'')
                    break
        else:
            newstring = newstring.replace(thousandseparator,'')
            ts = thousandseparator

        # check decimal symbol
        if decimalsign.strip() == 'auto':
            for ds in (",","p","."):
                if ds in newstring:
                    if newstring.count(ds) > 1 and 'j' not in newstring:
                        raise ValueError('the string format is incorrect: ' + string)
                    newstring = newstring.replace(ds,'.')
                    break
        else:
            if string.count(decimalsign) > 1:
                raise ValueError('the string format is incorrect: ' + string)
            newstring = newstring.replace(decimalsign,'.')
            ds = decimalsign

        if validate(string,ds=ds,ts=ts):
            return newstring

    if type(string) is str:
        # first, clean the string if is type str
        string = cleaner(string)

        # then, cast the string
        value = caster(string)

        # convert to integer numbers in scientific notation without decimals digits
        if 'E' in string.upper() and '.' not in string:
            if type(value) is float:
                if int(value) == value:
                    value = int(value)

        return value

    elif type(string) in (int,float,complex):
        return string

    else:
        raise TypeError('string must be a str or a number')