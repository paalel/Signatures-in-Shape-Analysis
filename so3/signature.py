from numpy import insert, zeros, sqrt, linspace, array, flip
from numpy import concatenate as np_concatenate, dot
from numpy.linalg import norm as np_norm
from iisignature import sig, logsig
from itertools import product
from math import factorial, pow
from .transformations import right_log, skew_to_vector, hatinv, Ad
from .curves import lift_piece_wise_constant

"""Signature stuff."""
def signature(path, k):
    return insert(sig(path, k), 0, 1.0, axis=0)

def curve_signature(c, k):
    is_multi = len(c.shape) == 4
    I = linspace(0,1, c.shape[1 if is_multi else 0])
    q = skew_to_vector(right_log(c, I))
    x = lift_piece_wise_constant(q,I)
    return signature(q, k)


""" Group metric """
def get_words(d, k):
    if not d or not k:
        raise("dimensions (d,k) not supplied")

    index = 0
    words = [[]]
    word_index =  { repr([]) : index }
    letters = range(d)
    for i in range(k):
        for word in product(letters, repeat=i+1):
            index += 1
            words.append(list(word))
            word_index[repr(list(word))] = index 

    return words, word_index

def split_word(word):
    n = len(word)
    l0 = [word[0:i] for i in range(n,-1,-1)]
    l1 = [word[i:] for i in range(n,-1,-1)]
    return [l0, l1]

def inverse_inner_product(sig0, sig1, word_index, word):
    l0, l1 = split_word(word)
    sum = 0.0
    for i in range(len(l1)):
        index0 = word_index[repr(l0[i])]
        index1 = word_index[repr(list(reversed(l1[i])))]
        sum += sig1[index1] * sig0[index0] * (-1.0 if len(l1[i]) % 2 else 1.0)

    return sum


def inverse_tensor_product(sig0, sig1, words=None, word_index=None, d=None, k=None):
    if not words or not word_index:
        words, word_index = get_words(d, k)

    tp = zeros((len(words)))
    for i, w in enumerate(words):
        tp[i] = inverse_inner_product(sig0, sig1, word_index, w)

    return tp 

def inverse_signature(sig, words, word_index, k, d):
    inv_sig = zeros(sig.shape)
    for i in range(sig.shape[0]):
        index = word_index[repr(list(reversed(words[i])))]
        inv_sig[index] = (-1.0 if len(words[i]) % 2 else 1.0) * sig[i]

    return inv_sig


def group_norm(tp, tp_inv, words, word_index, k, d):
    rem = [0.0]*k
    rem_inv = [0.0]*k
    for w in words[1:]:
        index = word_index[repr(w)]
        rem[len(w)-1] += tp[index]**2
        rem_inv[len(w)-1] += tp_inv[index]**2

    f = lambda r, i: pow(float(factorial(i))*sqrt(r), 1.0/i) if r > 10**(-16) else 0.0

    return (
              max(f(r,i+1) for i, r in enumerate(rem)) 
            + max(f(r,i+1) for i, r in enumerate(rem_inv))
           )


def group_metric(sig0, sig1, words=None, word_index=None, k=None, d=None):
    if not words or not word_index:
        words, word_index = get_words(d, k)

    tp = inverse_tensor_product(sig0, sig1, words, word_index)
    tp_inv = inverse_tensor_product(sig1, sig0, words, word_index)
    return group_norm(tp, tp_inv, words, word_index, k, d)

def concatenate_group_metric(c0, c1, words, word_index, k, d):
    is_multi = len(c0.shape) == 4
    I0 = linspace(0,1, c0.shape[1 if is_multi else 0])
    I1 = linspace(0,1, c1.shape[1 if is_multi else 0])

    c = concatenate_group(c0,c1)
    I = concatenate_time_stamps(I0,I1)
    q = skew_to_vector(right_log(c, I))
    x = lift_piece_wise_constant(q, I)
    sig = signature(x, k)
    inv_sig = inverse_signature(sig, words, word_index, k, d)
    return group_norm(sig, inv_sig, words, word_index, k, d)
