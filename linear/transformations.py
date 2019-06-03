from numpy import array, zeros, sqrt, dot
from numpy.linalg import norm
TOL = 0.00000000001

def diff(x0, x1, y0, y1):
    return (y1 - y0) / (x1- x0)

# SRVT:  Imm(I, SO3) -> C(I, so3\0)
# recursivly transform curves in SO3^d
def right_log(c, I):
    q = zeros(c.shape)
    for i in range(q.shape[0]-1):
        q[i] = diff(I[i], I[i+1], c[i], c[i+1])
    return q

# SRVT:  Imm(I, SO3) -> C(I, so3\0)
# recursivly transform curves in SO3^d
def SRVT(c, I):
    q = zeros(c.shape)
    for i in range(q.shape[0]-1):
        v = diff(I[i], I[i+1], c[i], c[i+1])
        n = sqrt(norm(v))
        if n < TOL:
            n = 1
        q[i] = v/n
    return q

# inverse SRVT: C(I, so3\0) -> C(I, SO3)
# recursivly transform curves in so3^d
def inverse_SRVT(q, I):
    c = zeros(q.shape)
    for i in range(c.shape[0]-1):
        c[i+1] = (I[i+1] - I[i]) * q[i] * norm(q[i]) + c[i]
    return c
