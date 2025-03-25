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
    return x * 1E+03

def ogf_MM(x):
    return x * 1E+06

def ogf_B(x):
    return x * 1E+09

def ogf_T(x):
    return x * 1E+12


## data prefixes
# bit

def data_bit_Y(x):
    return x * 1E+24

def data_bit_Z(x):
    return x * 1E+21

def data_bit_E(x):
    return x * 1E+18

def data_bit_P(x):
    return x * 1E+15

def data_bit_T(x):
    return x * 1E+12

def data_bit_G(x):
    return x * 1E+09

def data_bit_M(x):
    return x * 1E+06

def data_bit_K(x):
    return x * 1E+03

# byte

def data_byte_Y(x):
    return x * 2 ** 80

def data_byte_Z(x):
    return x * 2 ** 70

def data_byte_E(x):
    return x * 2 ** 60

def data_byte_P(x):
    return x * 2 ** 50

def data_byte_T(x):
    return x * 2 ** 40

def data_byte_G(x):
    return x * 2 ** 30

def data_byte_M(x):
    return x * 2 ** 20

def data_byte_K(x):
    return x * 2 ** 10


## SI prefixes
# linear quantities

def si_Q_1(x):
    return x * 1E+30

def si_R_1(x):
    return x * 1E+27

def si_Y_1(x):
    return x * 1E+24

def si_Z_1(x):
    return x * 1E+21

def si_E_1(x):
    return x * 1E+18

def si_P_1(x):
    return x * 1E+15

def si_T_1(x):
    return x * 1E+12

def si_G_1(x):
    return x * 1E+09

def si_M_1(x):
    return x * 1E+06

def si_k_1(x):
    return x * 1E+03

def si_h_1(x):
    return x * 1E+02

def si_da_1(x):
    return x * 1E+01

def si_d_1(x):
    return x * 1E-01

def si_c_1(x):
    return x * 1E-02

def si_m_1(x):
    return x * 1E-03

def si_u_1(x):
    return x * 1E-06

def si_n_1(x):
    return x * 1E-09

def si_p_1(x):
    return x * 1E-12

def si_f_1(x):
    return x * 1E-15

def si_a_1(x):
    return x * 1E-18

def si_z_1(x):
    return x * 1E-21

def si_y_1(x):
    return x * 1E-24

def si_r_1(x):
    return x * 1E-27

def si_q_1(x):
    return x * 1E-30


# areal quantities

def si_Q_2(x):
    return x * 1E+60

def si_R_2(x):
    return x * 1E+54

def si_Y_2(x):
    return x * 1E+48

def si_Z_2(x):
    return x * 1E+42

def si_E_2(x):
    return x * 1E+36

def si_P_2(x):
    return x * 1E+30

def si_T_2(x):
    return x * 1E+24

def si_G_2(x):
    return x * 1E+18

def si_M_2(x):
    return x * 1E+12

def si_k_2(x):
    return x * 1E+06

def si_h_2(x):
    return x * 1E+04

def si_da_2(x):
    return x * 1E+02

def si_d_2(x):
    return x * 1E-02

def si_c_2(x):
    return x * 1E-04

def si_m_2(x):
    return x * 1E-06

def si_u_2(x):
    return x * 1E-12

def si_n_2(x):
    return x * 1E-18

def si_p_2(x):
    return x * 1E-24

def si_f_2(x):
    return x * 1E-30

def si_a_2(x):
    return x * 1E-36

def si_z_2(x):
    return x * 1E-42

def si_y_2(x):
    return x * 1E-48

def si_r_2(x):
    return x * 1E-54

def si_q_2(x):
    return x * 1E-60


# volume quantities

def si_Q_3(x):
    return x * 1E+90

def si_R_3(x):
    return x * 1E+81

def si_Y_3(x):
    return x * 1E+72

def si_Z_3(x):
    return x * 1E+63

def si_E_3(x):
    return x * 1E+54

def si_P_3(x):
    return x * 1E+45

def si_T_3(x):
    return x * 1E+36

def si_G_3(x):
    return x * 1E+27

def si_M_3(x):
    return x * 1E+18

def si_k_3(x):
    return x * 1E+09

def si_h_3(x):
    return x * 1E+06

def si_da_3(x):
    return x * 1E+03

def si_d_3(x):
    return x * 1E-03

def si_c_3(x):
    return x * 1E-06

def si_m_3(x):
    return x * 1E-09

def si_u_3(x):
    return x * 1E-18

def si_n_3(x):
    return x * 1E-27

def si_p_3(x):
    return x * 1E-36

def si_f_3(x):
    return x * 1E-45

def si_a_3(x):
    return x * 1E-54

def si_z_3(x):
    return x * 1E-63

def si_y_3(x):
    return x * 1E-72

def si_r_3(x):
    return x * 1E-81

def si_q_3(x):
    return x * 1E-90