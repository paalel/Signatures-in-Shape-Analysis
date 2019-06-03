import pylab as pl
from collections import defaultdict
from .animation import *

def Rx(a):
    s, c = pl.sin(a), pl.cos(a)
    return pl.array( [[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]] )

def Ry(a):
    s, c = pl.sin(a), pl.cos(a)
    return pl.array( [[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]] )

def Rz(a):
    s, c = pl.sin(a), pl.cos(a)
    return pl.array( [[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]] )

def T(t):
    M = eye(4)
    M[:3,3] = t
    return M

class Bone(object):
    def __init__(self):
        self.name = ''
        self.direction = zeros(3)
        self.length = 0.
        self.axis = zeros(3)
        self.dof = []
        self.limits = []

class Skeleton(object):
    SCALE = 0.05

    def __init__(self, description = ""):
        self._description = description
        self.bones = dict()
        self.__local_matrices = None
        self.hierarchy = defaultdict(set)
        self.root = 'root'
        self._lines = None
        self._coords = None 

    def precompute_local_matrices(self):
        self.__local_matrices = dict()

        for key, bone in self.bones.items():
            C = dot(Rz(bone.axis[2]), dot(Ry(bone.axis[1]), Rx(bone.axis[0])))
            Cinv = C.transpose()
            B = T(bone.direction * bone.length)

            self.__local_matrices[key+'__C'] = C
            self.__local_matrices[key+'__Cinv'] = Cinv
            self.__local_matrices[key+'__B'] = B

    def setup_skeleton_neutral_coords(self):
        coords = [zeros(3)]
        def get_child_coords(bone, pos):
            for child in self.hierarchy[bone]:
                cbone = self.bones[child]
                cpos = pos + cbone.direction * cbone.length
                coords.append(cpos)
                get_child_coords(child, cpos)

        get_child_coords('root', zeros(3))
        self._coords = coords

    def get_skeleton_neutral_coords(self):
        if self._coords is None:
            self.setup_skeleton_neutral_coords()

        return pl.vstack(self._coords).T

    def setup_skeleton_neutral_lines(self):
        lines = []

        def traverse_hierarchy(bone, bcount):
            ncount = bcount
            for child in self.hierarchy[bone]:
                lines.append([bcount, ncount + 1])
                ncount = traverse_hierarchy(child, ncount + 1)

            return ncount

        traverse_hierarchy('root', 0)
        self._lines = lines

    def get_skeleton_neutral_lines(self):
        if self._lines is None:
            self.setup_skeleton_neutral_lines()

        return self._lines

    def get_coords_for_frame(self, frame, root_offset = None):
        coords = []
        def draw_line_to_children(bone, ppos, P, rpos, ppindex):
            for child in self.hierarchy[bone]:
                cbone = self.bones[child]
                C = self.__local_matrices[child + '__C']
                Cinv = self.__local_matrices[child + '__Cinv']
                B = self.__local_matrices[child + '__B']

                #Motion matrix
                M = eye(4)
                try:
                    for dof, val in zip(cbone.dof, frame[child]):
                        val = pl.deg2rad(val)
                        R = eye(4)
                        if dof == 'rx':
                            R = Rx(val)
                        elif dof == 'ry':
                            R = Ry(val)
                        elif dof == 'rz':
                            R = Rz(val)

                        M = dot(R,M)
                except: #We might not have dof data for the current bone
                    pass

                L = C.dot(M).dot(Cinv).dot(B)

                #Full transform
                A = dot(P, L)

                cpos = dot(A, [0,0,0,1]) + rpos

                coords.append(cpos[:3])
                draw_line_to_children(child, cpos, A, rpos, len(coords) - 1)

        #Root orientation and translation
        transf = frame['root'].copy()
        if root_offset is not None:
            transf[0:3] += root_offset

        R = dot(Rz(pl.deg2rad(transf[5])), dot(Ry(pl.deg2rad(transf[4])), Rx(pl.deg2rad(transf[3]))))
        B = T(transf[0:3])
        rpos = dot(B, [0,0,0,1])/0.45 * Skeleton.SCALE
        coords.append(rpos[:3])

        draw_line_to_children('root', rpos, R, rpos, 0)

        return pl.vstack(coords).T

    def get_lines_for_frame(self, frame, root_offset = None):
        lines = []
        def draw_line_to_children(bone, ppos, P, rpos):
            for child in self.hierarchy[bone]:
                cbone = self.bones[child]

                C = self.__local_matrices[child + '__C']
                Cinv = self.__local_matrices[child + '__Cinv']
                B = self.__local_matrices[child + '__B']

                #Motion matrix
                M = eye(4)
                try:
                    for dof, val in zip(cbone.dof, frame[child]):
                        val = pl.deg2rad(val)
                        R = eye(4)
                        if dof == 'rx':
                            R = Rx(val)
                        elif dof == 'ry':
                            R = Ry(val)
                        elif dof == 'rz':
                            R = Rz(val)

                        #M = dot(M, R)
                        M = dot(R,M)
                except: #We might not have dof data for the current bone
                    pass

                #Local transform
                L = C.dot(M).dot(Cinv).dot(B)
                #Full transform
                A = dot(P, L)

                cpos = dot(A, [0,0,0,1]) + rpos

                if child[0] == 'rtoes' or child == 'ltoes':
                    continue

                lines.append([ppos[:3], cpos[:3]])

                draw_line_to_children(child, cpos, A, rpos)

        #Root orientation and translation
        transf = frame['root'].copy()
        if root_offset is not None:
            transf[0:3] += root_offset

        R = dot(Rz(pl.deg2rad(transf[5])), dot(Ry(pl.deg2rad(transf[4])), Rx(pl.deg2rad(transf[3]))))
        B = T(transf[0:3])
        rpos = dot(B, [0,0,0,1])/0.45 * Skeleton.SCALE
        draw_line_to_children('root', rpos, R, rpos)

        return lines
