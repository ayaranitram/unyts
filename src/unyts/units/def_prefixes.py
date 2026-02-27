#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 03 23:15:37 2024

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.1.1'
__release__ = 20250324


# oil and gas field prefixes

def ogf_M(x):
    """Oil and Gas Field prefix for 1E+06 (M) volume units."""
    return x * 1E+03

def ogf_MM(x):
    """Oil and Gas Field prefix for 1E+06 (MM) volume units."""
    return x * 1E+06

def ogf_B(x):
    """Oil and Gas Field prefix for 1E+09 (B) volume units."""
    return x * 1E+09

def ogf_T(x):
    """Oil and Gas Field prefix for 1E+12 (T) volume units."""
    return x * 1E+12


## data prefixes
# bit

def data_bit_Y(x):
    """Data prefix for 1E+24 (Yotta)."""
    return x * 1E+24

def data_bit_Z(x):
    """Data prefix for 1E+21 (Zetta)."""
    return x * 1E+21

def data_bit_E(x):
    """Data prefix for 1E+18 (Exa)."""
    return x * 1E+18

def data_bit_P(x):
    """Data prefix for 1E+15 (Peta)."""
    return x * 1E+15

def data_bit_T(x):
    """Data prefix for 1E+12 (Tera)."""
    return x * 1E+12

def data_bit_G(x):
    """Data prefix for 1E+09 (Giga)."""
    return x * 1E+09

def data_bit_M(x):
    """Data prefix for 1E+06 (Mega)."""
    return x * 1E+06

def data_bit_K(x):
    """Data prefix for 1E+03 (Kilo)."""
    return x * 1E+03

# byte

def data_byte_Y(x):
    """Data prefix for 1E+24 (Yotta)."""
    return x * 2 ** 80

def data_byte_Z(x):
    """Data prefix for 1E+21 (Zetta)."""
    return x * 2 ** 70

def data_byte_E(x):
    """Data prefix for 1E+18 (Exa)."""
    return x * 2 ** 60

def data_byte_P(x):
    """Data prefix for 1E+15 (Peta)."""
    return x * 2 ** 50

def data_byte_T(x):
    """Data prefix for 1E+12 (Tera)."""
    return x * 2 ** 40

def data_byte_G(x):
    """Data prefix for 1E+09 (Giga)."""
    return x * 2 ** 30

def data_byte_M(x):
    """Data prefix for 1E+06 (Mega)."""
    return x * 2 ** 20

def data_byte_K(x):
    """Data prefix for 1E+03 (Kilo)."""
    return x * 2 ** 10


## SI prefixes
# linear quantities

def si_Q_1(x):
    """SI prefix for 1E+30 (Quetta) for linear quantities."""
    return x * 1E+30

def si_R_1(x):
    """SI prefix for 1E+27 (Ronna) for linear quantities."""
    return x * 1E+27

def si_Y_1(x):
    """SI prefix for 1E+24 (Yotta) for linear quantities."""
    return x * 1E+24

def si_Z_1(x):
    """SI prefix for 1E+21 (Zetta) for linear quantities."""
    return x * 1E+21

def si_E_1(x):
    """SI prefix for 1E+18 (Exa) for linear quantities."""
    return x * 1E+18

def si_P_1(x):
    """SI prefix for 1E+15 (Peta) for linear quantities."""
    return x * 1E+15

def si_T_1(x):
    """SI prefix for 1E+12 (Tera) for linear quantities."""
    return x * 1E+12

def si_G_1(x):
    """SI prefix for 1E+09 (Giga) for linear quantities."""
    return x * 1E+09

def si_M_1(x):
    """SI prefix for 1E+06 (Mega) for linear quantities."""
    return x * 1E+06

def si_k_1(x):
    """SI prefix for 1E+03 (Kilo) for linear quantities."""
    return x * 1E+03

def si_h_1(x):
    """SI prefix for 1E+02 (Hecto) for linear quantities."""
    return x * 1E+02

def si_da_1(x):
    """SI prefix for 1E+01 (Deca) for linear quantities."""
    return x * 1E+01

def si_d_1(x):
    """SI prefix for 1E-01 (Deci) for linear quantities."""
    return x * 1E-01

def si_c_1(x):
    """SI prefix for 1E-02 (Centi) for linear quantities."""
    return x * 1E-02

def si_m_1(x):
    """SI prefix for 1E-03 (Milli) for linear quantities."""
    return x * 1E-03

def si_u_1(x):
    """SI prefix for 1E-06 (Micro) for linear quantities."""
    return x * 1E-06

def si_n_1(x):
    """SI prefix for 1E-09 (Nano) for linear quantities."""
    return x * 1E-09

def si_p_1(x):
    """SI prefix for 1E-12 (Pico) for linear quantities."""
    return x * 1E-12

def si_f_1(x):
    """SI prefix for 1E-15 (Femto) for linear quantities."""
    return x * 1E-15

def si_a_1(x):
    """SI prefix for 1E-18 (Atto) for linear quantities."""
    return x * 1E-18

def si_z_1(x):
    """SI prefix for 1E-21 (Zepto) for linear quantities."""
    return x * 1E-21

def si_y_1(x):
    """SI prefix for 1E-24 (Yocto) for linear quantities."""
    return x * 1E-24

def si_r_1(x):
    """SI prefix for 1E-27 (Ronto) for linear quantities."""
    return x * 1E-27

def si_q_1(x):
    """SI prefix for 1E-30 (Quecto) for linear quantities."""
    return x * 1E-30


# areal quantities

def si_Q_2(x):
    """SI prefix for 1E+30^2 (Quetta) for areal quantities."""
    return x * 1E+60

def si_R_2(x):
    """SI prefix for 1E+27^2 (Ronna) for areal quantities."""
    return x * 1E+54

def si_Y_2(x):
    """SI prefix for 1E+24^2 (Yotta) for areal quantities."""
    return x * 1E+48

def si_Z_2(x):
    """SI prefix for 1E+21^2 (Zetta) for areal quantities."""
    return x * 1E+42

def si_E_2(x):
    """SI prefix for 1E+18^2 (Exa) for areal quantities."""
    return x * 1E+36

def si_P_2(x):
    """SI prefix for 1E+15^2 (Peta) for areal quantities."""
    return x * 1E+30

def si_T_2(x):
    """SI prefix for 1E+12^2 (Tera) for areal quantities."""
    return x * 1E+24

def si_G_2(x):
    """SI prefix for 1E+9^2 (Giga) for areal quantities."""
    return x * 1E+18

def si_M_2(x):
    """SI prefix for 1E+6^2 (Mega) for areal quantities."""
    return x * 1E+12

def si_k_2(x):
    """SI prefix for 1E+03^2 (Kilo) for areal quantities."""
    return x * 1E+06

def si_h_2(x):
    """SI prefix for 1E+02^2 (Hecto) for areal quantities."""
    return x * 1E+04

def si_da_2(x):
    """SI prefix for 1E+01^2 (Deca) for areal quantities."""
    return x * 1E+02

def si_d_2(x):
    """SI prefix for 1E-01^2 (Deci) for areal quantities."""
    return x * 1E-02

def si_c_2(x):
    """SI prefix for 1E-02^2 (Centi) for areal quantities."""
    return x * 1E-04

def si_m_2(x):
    """SI prefix for 1E-03^2 (Milli) for areal quantities."""
    return x * 1E-06

def si_u_2(x):
    """SI prefix for 1E-06^2 (Micro) for areal quantities."""
    return x * 1E-12

def si_n_2(x):
    """SI prefix for 1E-09^2 (Nano) for areal quantities."""
    return x * 1E-18

def si_p_2(x):
    """SI prefix for 1E-12^2 (Pico) for areal quantities."""
    return x * 1E-24

def si_f_2(x):
    """SI prefix for 1E-15^2 (Femto) for areal quantities."""
    return x * 1E-30

def si_a_2(x):
    """SI prefix for 1E-18^2 (Atto) for areal quantities."""
    return x * 1E-36

def si_z_2(x):
    """SI prefix for 1E-21^2 (Zepto) for areal quantities."""
    return x * 1E-42

def si_y_2(x):
    """SI prefix for 1E-24^2 (Yocto) for areal quantities."""
    return x * 1E-48

def si_r_2(x):
    """SI prefix for 1E-27^2 (Ronto) for areal quantities."""
    return x * 1E-54

def si_q_2(x):
    """SI prefix for 1E-30^2 (Quecto) for areal quantities."""
    return x * 1E-60


# volume quantities

def si_Q_3(x):
    """SI prefix for 1E+30^3 (Quetta) for volume quantities."""
    return x * 1E+90

def si_R_3(x):
    """SI prefix for 1E+27^3 (Ronna) for volume quantities."""
    return x * 1E+81

def si_Y_3(x):
    """SI prefix for 1E+24^3 (Yotta) for volume quantities."""
    return x * 1E+72

def si_Z_3(x):
    """SI prefix for 1E+21^3 (Zetta) for volume quantities."""
    return x * 1E+63

def si_E_3(x):
    """SI prefix for 1E+18^3 (Exa) for volume quantities."""
    return x * 1E+54

def si_P_3(x):
    """SI prefix for 1E+15^3 (Peta) for volume quantities."""
    return x * 1E+45

def si_T_3(x):
    """SI prefix for 1E+12^3 (Tera) for volume quantities."""
    return x * 1E+36

def si_G_3(x):
    """SI prefix for 1E+09^3 (Giga) for volume quantities."""
    return x * 1E+27

def si_M_3(x):
    """SI prefix for 1E+06^3 (Mega) for volume quantities."""
    return x * 1E+18

def si_k_3(x):
    """SI prefix for 1E+03^3 (Kilo) for volume quantities."""
    return x * 1E+09

def si_h_3(x):
    """SI prefix for 1E+02^3 (Hecto) for volume quantities."""
    return x * 1E+06

def si_da_3(x):
    """SI prefix for 1E+01^3 (Deca) for volume quantities."""
    return x * 1E+03

def si_d_3(x):
    """SI prefix for 1E-01^3 (Deci) for volume quantities."""
    return x * 1E-03

def si_c_3(x):
    """SI prefix for 1E-02^3 (Centi) for volume quantities."""
    return x * 1E-06

def si_m_3(x):
    """SI prefix for 1E-03^3 (Milli) for volume quantities."""
    return x * 1E-09

def si_u_3(x):
    """SI prefix for 1E-06^3 (Micro) for volume quantities."""
    return x * 1E-18

def si_n_3(x):
    """SI prefix for 1E-09^3 (Nano) for volume quantities."""
    return x * 1E-27

def si_p_3(x):
    """SI prefix for 1E-12^3 (Pico) for volume quantities."""
    return x * 1E-36

def si_f_3(x):
    """SI prefix for 1E-15^3 (Femto) for volume quantities."""
    return x * 1E-45

def si_a_3(x):
    """SI prefix for 1E-18^3 (Atto) for volume quantities."""
    return x * 1E-54

def si_z_3(x):
    """SI prefix for 1E-21^3 (Zepto) for volume quantities."""
    return x * 1E-63

def si_y_3(x):
    """SI prefix for 1E-24^3 (Yocto) for volume quantities."""
    return x * 1E-72

def si_r_3(x):
    """SI prefix for 1E-27^3 (Ronto) for volume quantities."""
    return x * 1E-81

def si_q_3(x):
    """SI prefix for 1E-30^3 (Quecto) for volume quantities."""
    return x * 1E-90