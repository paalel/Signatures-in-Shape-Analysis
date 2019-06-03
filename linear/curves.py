from numpy import linspace, array, zeros, array_equal, sqrt, sum, unique, concatenate
from numpy.linalg import norm
from dynamic_distance import find_optimal_diffeomorphism
from  transformations import SRVT, inverse_SRVT
from iisignature import sig


#calculate distance between two curves in the shape space using the SRVT 
def distance(c0, c1, I0=None, I1=None):
    if I0 is None:
        I0 = linspace(0,1, c0.shape[0])
    if I1 is None:
        I1 = linspace(0,1, c1.shape[0])

    q0 = SRVT(move_origin_to_zero(c0), I0)
    q1 = SRVT(move_origin_to_zero(c1), I1)

    return L2_metric(q0, q1, I0, I1)

#calculate the distance between two curves in P by using the DP algoritm 
#to find their optimal representative in S. Assumes that both curves have
#the same parameterization
def dynamic_distance(c0, c1, depth = 5):
    '''Uses DP algorithm to find an optimal alignment from c1 to c0 and
    returns a corresponding reparametrization of c1.'''
    I0 = linspace(0,1, c0.shape[0])
    I1 = linspace(0,1, c1.shape[0])

    q0 = SRVT(move_origin_to_zero(c0), I0)
    q1 = SRVT(move_origin_to_zero(c1), I1)

    I1_new = find_optimal_diffeomorphism(q0, q1, I0, I1, depth)
    c1_new = reparameterize(I1_new, I1, c1)
    return distance(c0, c1_new, I0 = I0, I1 = I1)

def optimal_reparameterization(c0, c1, depth = 5):
    '''Uses DP algorithm to find an optimal alignment from c1 to c0 and
    returns a corresponding reparametrization of c1.'''
    I0 = linspace(0,1, c0.shape[0])
    I1 = linspace(0,1, c1.shape[0])

    q0 = SRVT(move_origin_to_zero(c0), I0)
    q1 = SRVT(move_origin_to_zero(c1), I1)

    I1_new = find_optimal_diffeomorphism(q0, q1, I0, I1, depth)
    return reparameterize(I1_new, I1, c1)


def move_origin_to_zero(c):
    c_new = zeros(c.shape)
    for i in range(c.shape[0]):
        c_new[i] = c[i] - c[0]
    return c_new


# Reparameterize curve c by finding which subinterval in I a new point phi
# belongs to and then creating a the new point by linearly interpolating.
# Modulo N will allow us to potensially shift the start or end point in case of
# a closed curve.
def reparameterize(I_new, I, c):
    c_new = zeros(c.shape)
    N = c.shape[0]
    c_new[0], c_new[-1] = c[0], c[-1]

    j = 0
    for i in range(1,c.shape[0]-1):
        phi = I_new[i]
        while phi > I[j+1]:
            j += 1

        s = (phi - I[j]) / (I[j+1] - I[j])
        c_new[i] = c[j] + s * (c[j+1] - c[j])

    return c_new

# Calculate L2-metric of piece-wise constant q0 and q1:
# that is sqrt(integral( || q0 - q1 ||^2))
# assumes I0 and I1 increasing with:
# I0[0] = I1[0] and I0[-1] = I1[-1]
def L2_metric(q0, q1, I0, I1):
    if array_equal(I0, I1):
        return sqrt(sum(
            (I0[k+1]-I0[k])*(norm(q0[k]-q1[k])**2) for k in range(I0.shape[0]-1)
        ))

    #create array of shared interpolation points
    I = unique(concatenate((I0, I1)))
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

