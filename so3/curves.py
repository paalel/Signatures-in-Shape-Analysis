from numpy import linspace, array, dot, zeros, array_equal, flip
from numpy import sqrt, sum, unique, concatenate as np_concatenate
from .dynamic_distance import find_optimal_diffeomorphism
from .transformations import skew_to_vector, SRVT, inverse_SRVT
from .transformations import interpolate as tf_interpolate, gradient_close_curve
from .helpers import is_3x3_matrix, norm

"""Transformations applied to curves."""
#calculate distance between two curves in the shape space using the SRVT
def distance(c0, c1, I0=None, I1=None):

    is_multi = len(c0.shape) == 4
    if I0 is None:
        I0 = linspace(0,1, c0.shape[1 if is_multi else 0])
    if I1 is None:
        I1 = linspace(0,1, c1.shape[1 if is_multi else 0])

    q0 = skew_to_vector(SRVT(c0, I0))
    q1 = skew_to_vector(SRVT(c1, I1))

    return L2_metric(q0, q1, I0, I1)


def reparameterize_to_optimal(c0, c1, depth = 5):
    '''Uses DP algorithm to find an optimal alignment from c1 to c0 and
    returns a corresponding reparametrization of c1.'''
    is_multi = len(c0.shape) == 4
    I0 = linspace(0,1, c0.shape[1 if is_multi else 0])
    I1 = linspace(0,1, c1.shape[1 if is_multi else 0])

    q0 = skew_to_vector(SRVT(c0, I0))
    q1 = skew_to_vector(SRVT(c1, I1))

    I1_new = find_optimal_diffeomorphism(q0, q1, I0, I1, depth)
    return reparameterize(I1_new, I1, c1)


#calculate the distance between two curves in P by using the DP algoritm 
#to find their optimal representative in S. Assumes that both curves have
#the same parameterization
def dynamic_distance(c0, c1, depth = 5):
    '''Uses DP algorithm to find an optimal alignment from c1 to c0 and
    returns a corresponding reparametrization of c1.'''
    is_multi = len(c0.shape) == 4
    I0 = linspace(0,1, c0.shape[1 if is_multi else 0])
    I1 = linspace(0,1, c1.shape[1 if is_multi else 0])

    q0 = skew_to_vector(SRVT(c0, I0))
    q1 = skew_to_vector(SRVT(c1, I1))

    I1_new = find_optimal_diffeomorphism(q0, q1, I0, I1, depth)
    c1_new = reparameterize(I1_new, I1, c1)
    return distance(c0, c1_new, I0 = I0, I1 = I1)


def move_origin_to_zero(c):
    if len(c.shape) == 4:
        return array([move_origin_to_zero(e) for e in c])

    return array([dot(matrix, c[0].T) for matrix in c])

#linearly interpolate between two curves using SRVT and Inverse SRVT
#this can proably be written in the usual recursive form
def interpolate(c0, c1, s):
    if len(c0.shape) == 4:
        d, N, _, _ = c0.shape
        I = linspace(0, 1, N)
        q = array([(1-s)*SRVT(c0[i], I) + s*SRVT(c1[i], I) for i in range(d)])
        return array([inverse_SRVT(q[i], I) for i in range(d)])
    else:
        I = linspace(0,1, c0.shape[0])
        q = (1-s)*SRVT(c0, I) + s*SRVT(c1,I)
        return inverse_SRVT(q, I)

# Reparameterize curve c by finding which subinterval in I a new point phi
# belongs to and then creating a the new point by linearly interpolating.
# Modulo N will allow us to potensially shift the start or end point in case of
# a closed curve.
def reparameterize(I_new, I, c):
    if len(c.shape) == 4:
        return array([reparameterize(I_new, I, e) for e in c])

    c_new = zeros(c.shape)
    N = c.shape[0]

    j = 0
    for i in range(N):
        phi = I_new[i]
        while not I[j % N] <= phi <= I[(j+1) % N]:
            j += 1
            if j > 5*N:
                raise Exception("Could not place t_0 <= phi < t_1 in reparameterize")

        s = (phi - I[j % N]) / (I[(j+1) % N] - I[j % N])
        c_new[i] = tf_interpolate(c[j % N], c[(j+1) % N], s)

    return c_new


#close cuvre using gradient descent
def close(c, iterations = 25, alpha = 0.025, move_origin = False):
    if move_origin:
        c = move_origin_to_zero(c)

    is_multi = len(c.shape) == 4
    I = linspace(0,1, c.shape[1 if is_multi else 0])

    q = SRVT(c, I)
    for k in range(iterations):
        q -= alpha*gradient_close_curve(q, I)

    return inverse_SRVT(q, I)


# Calculate L2-metric of piece-wise constant q0 and q1:
# that is sqrt(integral( || q0 - q1 ||^2))
# assumes q in vector form.
# assumes I0 and I1 increasing with:
# I0[0] = I1[0] and I0[-1] = I1[-1]
def L2_metric(q0, q1, I0, I1):
    if array_equal(I0, I1):
        return sqrt(sum(
            (I0[k+1]-I0[k])*(norm(q0[k]-q1[k])**2) for k in range(I0.shape[0]-1)
        ))

    #create array of shared interpolation points
    I = unique(np_concatenate((I0, I1)))
    i,j = 0,0
    l2_sum = 0.0

    #interpolate to previous when creating diff
    for k in range(I.shape[0]-1):
        l2_sum += (I[k+1] - I[k]) * (norm(q0[i] - q1[j])**2)

        if I0[i+1] <= I[k+1]:
            i +=1
        if I1[j+1] <= I[k+1]:
            j +=1

    return sqrt(l2_sum)

"""Signatures specific mehtods"""
# Lift from piece wise constant to piece wise linear curve in R^3*d
# Ensures that the curve is in the format expected by the iisignature package.
# Assume x(0) = 0, the signature is translation invariant
def lift_piece_wise_constant(q, I):
    x = zeros(q.shape)

    for i in range(q.shape[1]-1):
        x[i+1] = q[i]*(I[i+1] - I[i]) + x[i]

    return x
