import sys
sys.path.append("../../")
from se3.transformations import *
from so3.transformations import Ry, Rx, Rz

import matplotlib.pyplot as plt
import numpy as np
from numpy.linalg import norm

n = 1000


#Test whether exp(log(r)) = r
diff_R = np.zeros(n)
diff_I = np.zeros(n)
I = np.eye(4)
lin = np.linspace(0, 2*3.14, n)
for i, v in enumerate(lin):
    R = np.eye(4)
    R[0:3,0:3] = Ry(v)
    R[3,2] = v
    I[3,2] = v
    r = rig_log(R)
    diff_R[i] = max((rig_exp(r) - R).flatten())
    diff_I[i] = max((rig_exp(r) - I).flatten())

plt.plot(lin, diff_R, label="difference compared to R")
plt.plot(lin, diff_I, label="difference compared to I")
plt.legend()
plt.show()


#Test that the interpolation is linear between R0 and R1
n = 1000
diff_R0 = np.zeros(n)
diff_R1 = np.zeros(n)
R0 = np.eye(4)
R1 = np.eye(4)
R0[0:3,0:3] = Ry(0)
R1[0:3,0:3] = Ry(2*3.14)
R0[3,0] = -0.4
R1[3,1] = 1
R1[3,2] = 100
for i, v in enumerate(np.linspace(0, 1, n)):
    r = interpolate(R0, R1, v)
    diff_R0[i] = norm((r - R0), ord="fro")
    diff_R1[i] = norm((r - R1), ord="fro")


plt.plot(lin, diff_R0, label="difference compared to R0")
plt.plot(lin, diff_R1, label="difference compared to R1")
plt.legend()
plt.show()

