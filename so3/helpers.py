from numpy import stack, interp as np_interp, array, sqrt, trace, dot
from numpy.linalg import norm as np_norm

TOL = 0.000000000001

#interpolate a multi dim array on the form fp: R -> R^n
def interp(x, xp, fp):
    return stack((np_interp(x, xp, array([f[i] for f in fp])) for i in range(fp.shape[1])), -1)


#norm of element in so3 (Lie algebra)
#frobinous norm for hatted isomoprhism and 2 norm are equivalent
def norm(r):
    if r.shape is (3,3):
        return sqrt(0.5*trace(dot(r,r.T)))
    return np_norm(r, ord=2)


#crop curve
def crop_curve(c, start=0, step=1, stop = None):
    if stop or start != 0:
        if len(c.shape) == 4:
            return array([e[start:stop:step] for e in c])
        else:
            return c[start:stop:step]
    return c
