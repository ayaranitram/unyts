# -*- coding: utf-8 -*-
"""
Created on Wed Aug  3 21:14:44 2022

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.5'
__release__ = 20221226
__all__ = ['caster', 'to_number']


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


def to_number(string, decimal_sign='auto', thousand_separator='auto', parenthesis_means_negative=True):
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
    decimal_sign : str
        The string used as decimal symbol.
    thousand_separator : str
        The string used as thousands separator.
    parenthesis_means_negative : bool
        True to cast numbers between parenthesis as negative, i.e. (15) = -15

    Returns
    -------
    None.

    """

    def cleaner(string):
        """
        Helper function to clean the string before attempting to cast

        Parameters
        ----------
        string : str

        Returns
        -------
            string : the cleaned string

        """

        def validate(string, ds, ts):
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
                for s in ('+', '-'):
                    if s in string.strip('+-'):
                        return check(string.strip('+-').split(s)[0]) and check(string.strip('+-').split(s)[1])
            else:
                return check(string)

        string = string.strip().lower()
        new_string = string

        # check parenthesis means negative
        if parenthesis_means_negative:
            if '(' in new_string:
                if ')' not in new_string:
                    raise ValueError('the string format is incorrect: ' + string)
                elif 'j' in new_string:
                    pass
                else:
                    if new_string.count('(') == 1 and new_string.count(')') == 1:
                        if new_string[0] == '(' and new_string[-1] == ')':
                            if '-' not in new_string:
                                new_string = '-' + new_string.replace('(', '').replace(')', '')
                            else:
                                raise ValueError('the string format is incorrect: ' + string)
            elif ')' in new_string:
                raise ValueError('the string format is incorrect: ' + string)
            else:
                pass

        # check thousands separator
        if thousand_separator in ('auto', '.') and decimal_sign in ('auto', ','):
            if ',' in new_string and '.' in new_string:
                if validate(string,ds=',',ts='.'):
                    new_string = new_string.replace('.', '').replace(',', '.')
                return new_string

        if thousand_separator.strip() == 'auto':
            for ts in ("'","`","´"," ",None):
                if ts is not None and ts in string:
                    new_string = new_string.replace(ts, '')
                    break
        else:
            new_string = new_string.replace(thousand_separator, '')
            ts = thousand_separator

        # check decimal symbol
        if decimal_sign.strip() == 'auto':
            for ds in (",","p","."):
                if ds in new_string:
                    if new_string.count(ds) > 1 and 'j' not in new_string:
                        raise ValueError('the string format is incorrect: ' + string)
                    new_string = new_string.replace(ds, '.')
                    break
        else:
            if string.count(decimal_sign) > 1:
                raise ValueError('the string format is incorrect: ' + string)
            new_string = new_string.replace(decimal_sign, '.')
            ds = decimal_sign

        if validate(string, ds=ds, ts=ts):
            return new_string

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

    elif type(string) in (int, float, complex):
        return string

    else:
        raise TypeError('string must be a str or a number')