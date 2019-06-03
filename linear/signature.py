from numpy import insert, zeros, sqrt, flip, concatenate as np_concatenate, power
from numpy.linalg import norm as np_norm
from iisignature import sig, prepare, logsig
from itertools import product
from math import factorial, pow
from transformations import right_log

"""Signature stuff."""
def signature(path, k):
    return insert(sig(path, k), 0, 1.0, axis=0)

def linear_metric(x,y):
    return np_norm(x - y)

def curve_signature(c, k):
    is_multi = len(c.shape) == 4
    I = linspace(0,1, c.shape[1 if is_multi else 0])
    q = skew_to_vector(right_log(c, I))
    return signature(q, k)

def signature(path, k):
    return insert(sig(path, k), 0, 1.0, axis=0)

def concatenate(x, y):
    return np_concatenate((x, (y[-2::-1]+x[-1]-y[-1])), axis=0)

def curve_concat_log_metric(x, y, s):
    return np_norm(logsig(concatenate(x ,y), s))

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

def inner_product(sig0, sig1, word_index, word):
    l0, l1 = split_word(word)
    sum = 0.0
    for i in range(len(l1)):
        index0 = word_index[repr(l1[i])]
        index1 = word_index[repr(list(reversed(l0[i])))]
        sign = -1.0 if len(l1[i]) % 2 else 1.0
        sum += sign * sig1[index1] * sig0[index0]

    return sum


def tensor_product(sig0, sig1, words=None, word_index=None, d=None, k=None):
    if not words or not word_index:
        words, word_index = get_words(d, k)

    tp = zeros((len(words)))
    for i, w in enumerate(words):
        tp[i] = inner_product(sig0, sig1, word_index, w)

    return tp 

def CC_distance(sig0, sig1, words=None, word_index=None, d=None, k=None):
    if not words or not word_index:
        words, word_index = get_words(d, k)
    tp = tensor_product(sig0, sig1, words, word_index)

    rem = [0.0]*k
    for w in words[1:]:
        index = word_index[repr(w)]
        rem[len(w)-1] += tp[index]**2

    f = lambda r, i: power(factorial(i)*sqrt(r), 1.0/i)
    return max(f(r,i+1) for i, r in enumerate(rem))


def distance(a,b, k, d):
    words, word_index = get_words(d, k)
    sig0 = signature(a, k)
    sig1 = signature(b, k)
    return CC_distance(sig0, sig1, words, word_index, d=d, k=k) + CC_distance(sig1, sig0, words, word_index, d=d, k=k)


def norm(c0, c1, s):
    sig0 = logsig(c0, s)
    sig1 = logsig(c1, s)
    return np_norm(sig0 - sig1)
