from numpy import array, isnan, zeros, eye, trace, dot
from numpy import sin, cos, arccos, sqrt
from numpy.linalg import norm
from .helpers import TOL, norm

""" Useful transformations in S03."""
#SO3 basis
def Rx(a):
    s, c = sin(a), cos(a)
    return array( [[1, 0, 0], [0, c, -s], [0, s, c]] )

def Ry(a):
    s, c = sin(a), cos(a)
    return array( [[c, 0, s], [0, 1, 0], [-s, 0, c]] )

def Rz(a):
    s, c = sin(a), cos(a)
    return array( [[c, -s, 0], [s, c, 0], [0, 0, 1]] )

#R3 <-> Lie algebra so3 -- ismoporhism
#recursivly map curves if necessary
def hat(v):
    if len(v.shape) == 4:
        return array([hat(curve) for curve in v])
    if len(v.shape) == 3:
        return array([hat(vector) for vector in v])
    return array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])

def hatinv(M):
    if len(M.shape) == 4:
        return array([hatinv(curve) for curve in M])
    if len(M.shape) == 3:
        return array([hatinv(matrix) for matrix in M])
    return array([-M[1,2], M[0,2], -M[0,1]])

#SO3 -> so3, R close to but not equal I
def rot_log(R):
    theta = arccos(0.5*(trace(R)-1))
    #When the angle is zero or NaN we can choose the element in so3 arbitrarily.
    # NaNs are known to be caused by rounding errors when calculating the trace
    # for the angle. Typically on the form trace(R) = 3.000000000000002 =>
    # theta = 0
    if abs(theta) < TOL or isnan(theta): return 0.5 * (R-R.T)
    return (theta/sin(theta)) * 0.5 * (R - R.T)

#so3 -> SO3
def rot_exp(r):
    theta = norm(r)
    if abs(theta) < TOL or isnan(theta): return eye(3)
    return eye(3) + (sin(theta)/theta)*r + ((1-cos(theta))/(theta**2))*dot(r,r)

#Adjoint operator: A^T*X*A
def Ad(A, X):
    return dot(dot(A.T, X), A)

#linearly interpolate between two close points in SO3
def interpolate(R0, R1, s=1):
    return dot(rot_exp(s*rot_log(dot(R1, R0.T))), R0)



"""Transformations applied to c in SO3 or q in so3.
c in I->SO3     : n x 3 x 3
c in I->SO3^d   : d x n x 3 x 3

matrix form:
q in I->so3     : n x 3 x 3
q in I->so3^d   : d x n x 3 x 3

vector form:
q in I->so3     : n x 3
q in I->so3^d   : n x 3*d
"""

# Right log derivative:  Imm(I, SO3) -> C(I, so3)
# recursivly transform curves in SO3^d
def right_log(c, I):
    if len(c.shape) == 4:
        return array([right_log(curve, I) for curve in c])

    n_frames  = c.shape[0]
    q = zeros((n_frames, 3,3))
    for i in range(n_frames-1):
        q[i] = rot_log(dot(c[i + 1], c[i].T)) / (I[i+1] - I[i])
    return q

# SRVT:  Imm(I, SO3) -> C(I, so3\0)
# recursivly transform curves in SO3^d
def SRVT(c, I):
    if len(c.shape) == 4:
        return array([SRVT(curve, I) for curve in c])

    n_frames  = c.shape[0]
    q = zeros((n_frames, 3,3))
    for i in range(n_frames-1):
        v = rot_log(dot(c[i + 1], c[i].T)) / (I[i+1] - I[i])
        n = sqrt(norm(v))
        if n < TOL:
            n = 1
        q[i] = v/n
    return q

# inverse SRVT: C(I, so3\0) -> C(I, SO3)
# recursivly transform curves in so3^d
def inverse_SRVT(q, I):
    if len(q.shape) == 4:
        return array([inverse_SRVT(curve, I) for curve in q])

    n_frames  = q.shape[0]
    c = zeros((n_frames,3,3))
    c[0] = eye(3)
    for i in range(n_frames-1):
        v =(I[i+1] - I[i])*norm(q[i])*q[i]
        c[i+1] = dot(rot_exp(v), c[i])
    return c

#Transform vector q to vector representation
# q: d x n x 3 x 3 ->
# hatinv -> d x n x 3 -> swapaxis -> n x d x 3 -> reshape ->
# q : n x 3*d
def skew_to_vector(q):
    if len(q.shape) == 4 and is_3x3_matrix(q):
        d, n, _, _ = q.shape
        return hatinv(q).swapaxes(0,1).reshape(n, 3*d)
    if len(q.shape) == 3 and is_3x3_matrix(q):
        return hatinv(q)

    raise Exception("Already vectorized in skew_to_vector")


#the gradient used to close a curve
def gradient_close_curve(q, I):
    if len(q.shape) == 4:
        return array([gradient_close_curve(e, I) for e in q])

    c = inverse_SRVT(q, I)
    grad = zeros((q.shape))
    res = rot_log(c[-1])

    for i in range(q.shape[0]):
        tmp = dot(c[i], dot(res, c[i].T))
        n = norm(q[i])
        if n < TOL or isnan(n):
            continue
        grad[i] = n*tmp + trace(dot(tmp.T, q[i]/n))*q[i]

    return grad
