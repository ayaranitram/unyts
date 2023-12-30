# -*- coding: utf-8 -*-
"""
Created on Wed Aug  3 21:14:44 2022

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.10'
__release__ = 20231230
__all__ = ['caster', 'to_number']

from .common_classes import number


def caster(string: str) -> number:
    """
    Helper function to try to cast the string to number.

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
        the cast number

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
                raise ValueError(f"could not convert string to number: {string}.")
    return value


def to_number(number_or_string: str, decimal_sign='auto', thousand_separator='auto',
              parenthesis_means_negative=True) -> number:
    """
    Cast a string the appropriate numeric type.
    Valid numbers are:
        integers
        real numbers
        complex numbers

    By default, automatically converts comma ',' to period '.' and remove a thousand separators

    Parameters
    ----------
    number_or_string : str
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

    def cleaner(str_to_clean: str):
        """
        Helper function to clean the string before attempting to cast

        Parameters
        ----------
        str_to_clean : str

        Returns
        -------
            string : the cleaned string

        """

        def validate(str_to_validate: str, ds, ts):
            """
            Helper function to validate the string format

            Parameters
            ----------
            str_to_validate : str
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

            def check(str_to_check: str):
                """
                count the number of decimal signs and thousand separators
                """
                if len(str_to_check.split(ds)) > 2 :
                    raise ValueError(f"The string format is incorrect: '{str_to_check}'.")
                if ts is not None:
                    for part in str_to_check.split(ds)[0].split(ts)[1:]:
                        if len(part) != 3:
                            raise ValueError(f"The string format is incorrect: '{str_to_check}'.")
                if 'e' in str_to_check:
                    if 'j' in str_to_check:
                        if str_to_check.count('j') > 1 or str_to_check[-1] != 'j':
                            raise ValueError(f"The string format is incorrect: '{str_to_check}'.")
                        if not str_to_check.split('e')[-1][:-1].isdigit():
                            raise ValueError(f"The string format is incorrect: '{str_to_check}'.")

                    elif not str_to_check.split('e')[-1].isdigit():
                        raise ValueError(f"The string format is incorrect: '{str_to_check}'.")
                return True

            if 'j' in str_to_validate:
                for s in ('+', '-'):
                    if s in str_to_validate.strip('+-'):
                        return check(str_to_validate.strip('+-').split(s)[0]) \
                            and check(str_to_validate.strip('+-').split(s)[1])
            else:
                return check(str_to_validate)

        str_to_clean = str_to_clean.strip().lower()
        new_string = str_to_clean

        # check parenthesis means negative
        if parenthesis_means_negative:
            if '(' in new_string:
                if ')' not in new_string:
                    raise ValueError(f"The string format is incorrect: '{str_to_clean}'.")
                elif 'j' in new_string:
                    pass
                else:
                    if new_string.count('(') == 1 and new_string.count(')') == 1:
                        if new_string[0] == '(' and new_string[-1] == ')':
                            if '-' not in new_string:
                                new_string = '-' + new_string.replace('(', '').replace(')', '')
                            else:
                                raise ValueError(f"The string format is incorrect: '{str_to_clean}'.")
            elif ')' in new_string:
                raise ValueError(f"The string format is incorrect: '{str_to_clean}'.")
            else:
                pass

        # check thousands separator
        if thousand_separator in ('auto', '.') and decimal_sign in ('auto', ','):
            if ',' in new_string and '.' in new_string:
                if validate(str_to_clean, ds=',', ts='.'):
                    new_string = new_string.replace('.', '').replace(',', '.')
                return new_string

        if thousand_separator.strip() == 'auto':
            for ts in ("'","`","´"," ",None):
                if ts is not None and ts in str_to_clean:
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
                        raise ValueError(f"The string format is incorrect: '{str_to_clean}'.")
                    new_string = new_string.replace(ds, '.')
                    break
        else:
            if str_to_clean.count(decimal_sign) > 1:
                raise ValueError(f"The string format is incorrect: '{str_to_clean}'.")
            new_string = new_string.replace(decimal_sign, '.')
            ds = decimal_sign

        if validate(str_to_clean, ds=ds, ts=ts):
            return new_string

    if type(number_or_string) is str:
        # first, clean the string if is type str
        number_or_string = cleaner(number_or_string)

        # then, cast the string
        value = caster(number_or_string)

        # convert to integer numbers in scientific notation without decimals digits
        if 'E' in number_or_string.upper() and '.' not in number_or_string:
            if type(value) is float:
                if int(value) == value:
                    value = int(value)

        return value

    elif type(number_or_string) in (int, float, complex):
        return number_or_string

    else:
        raise TypeError('str_to_clean must be str or numeric.')
