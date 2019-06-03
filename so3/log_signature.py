from numpy import insert, zeros, sqrt, linspace,array,flip
from numpy import concatenate as np_concatenate, dot
from numpy.linalg import norm as np_norm
from iisignature import sig, logsig
from itertools import product
from math import factorial, pow
from .transformations import right_log, skew_to_vector, hatinv, Ad
from .curves import lift_piece_wise_constant

"""Signature stuff."""
def log_signature(path, s):
    return logsig(path, s)

def curve_log_signature(c, s):
    is_multi = len(c.shape) == 4
    I = linspace(0,1, c.shape[1 if is_multi else 0])
    q = skew_to_vector(right_log(c, I))
    x = lift_piece_wise_constant(q,I)
    return log_signature(q, s)


""" Metrics """
def linear_metric(sig0, sig1):
    return np_norm(sig0 - sig1)

def normalized_linear_distance(sig0, sig1):
    a = np_norm(sig0)
    b = np_norm(sig1)
    div = lambda x: x if x > 0.0 else 1.0
    return np_norm(sig0/div(a) - sig1/div(b))

def concatenate_metric(c0, c1, s):
    I0 = linspace(0.0, 1.0, c0.shape[1])
    I1 = linspace(0.0, 1.0, c1.shape[1])
    
    q0 = skew_to_vector(right_log(c0, I0))
    q1 = skew_to_vector(right_log(c1, I1))

    u = np_concatenate((q0[:-1], flip(q1[:-1], axis=0)), axis=0)
    v = np_concatenate((q1[:-1], flip(q0[:-1], axis=0)), axis=0)

    Iu = np_concatenate((linspace(0,0.5, q0.shape[0]),linspace(0.5, 1, q1.shape[0])[1:]), axis = 0) 
    Iv = np_concatenate((linspace(0,0.5, q1.shape[0]),linspace(0.5, 1, q0.shape[0])[1:]), axis = 0) 

    x = lift_piece_wise_constant(u, Iu)
    y = lift_piece_wise_constant(v, Iv)
    return np_norm(log_signature(x, s)) + np_norm(log_signature(y, s))
