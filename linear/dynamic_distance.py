from numpy import zeros, inf, array, interp, sqrt, concatenate, linspace,array_equal, unique, where
from numpy.linalg import norm
from functools import partial

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

def create_shared_parameterization(q0, q1, I0, I1):
    if array_equal(I0, I1):
        return I0, q0, q1

    #create array of shared interpolation points
    I = unique(concatenate((I0, I1)))
    i,j = 0,0
    q0_new = zeros((I.shape[0], q0.shape[1]))
    q1_new = zeros((I.shape[0], q0.shape[1]))

    #interpolate to previous when creating diff
    for k in range(I.shape[0]-1):
        q0_new[k] = q0[i]
        q1_new[k] = q1[j]

        if I0[i+1] <= I[k+1]:
            i +=1
        if I1[j+1] <= I[k+1]:
            j +=1

    return I, q0_new, q1_new


def dynamic(local_cost, M, depth):
    '''Calculates the dynamic programming matrix.
    Returns a tuple (pointers, A) where A is the minimal energy matrix
    and pointers is a dict mapping indices (i,j) -> (k,l), where (k, l)
    is the optimal predecessor grid point as determined by DP.'''

    A = zeros((M,M))
    pointers = dict()

    for i in range(1, M):
        for j in range(1, M):
            min_cost = inf
            best_pred = None
            for pred in predecessors(i, j, depth):
                k, l = pred
                cost = local_cost(k, l, i, j) + A[k, l]
                if min_cost > cost:
                    min_cost = cost
                    best_pred = pred
            A[i, j] = min_cost
            pointers[(i,j)] = best_pred

    return pointers, A

def reconstruct(pointers, M, N):
    '''Implements the backtrace in the dynamic programming algorithm.'''
    path = [(M,N)]
    try:
        while True:
            pred = path[-1]
            path.append(pointers[pred])
    except:
        pass

    path.reverse()
    return path

def predecessors(i, j, depth):
    '''List of predecessor grid points considered at every gridpoint in the DP matrix.
    Strongly restricted to keep computational cost in check.'''
    for k in range(max(0, i-depth), i):
        for l in range(max(0, j-depth), j):
            yield (k,l) 


def local_cost(k, l, i, j, q0, q1, I):
    return L2_metric(
            q0[k:i+1],
            sqrt((I[j]-I[l])/(I[i]-I[k]))*q1[l:j+1],
            I[k:i+1],
            linspace(I[k], I[i], (j-l+1))
        )**2 



def find_optimal_diffeomorphism(q0, q1, I0, I1, depth):
    I, q0_new, q1_new = create_shared_parameterization(q0, q1, I0, I1)
    M = I.shape[0]
    local_cost_partial = partial(local_cost, q0 = q0_new, q1 = q1_new, I = I)

    pointers, A = dynamic(local_cost_partial, M, depth)
    path = reconstruct(pointers, M-1, M-1)

    #Construct reparametrization
    x = array([p[0] for p in path])/float(M-1)
    y = array([p[1] for p in path])/float(M-1)

    return interp(I1, x, y)
