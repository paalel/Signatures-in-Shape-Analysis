import pylab as pl
import sys

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
    M = pl.eye(4)
    M[:3,3] = t
    return M

def convert_to_SO3(skeleton, frame, filter_noisy_channels=False):
    def convert(node):
        if node is 'root':
            transf = [pl.deg2rad(x) for x in frame['root']]
            return pl.dot(Rz(transf[5]), pl.dot(Ry(transf[4]), Rx(transf[3])))


        cbone = skeleton.bones[node]
        #Motion matrix
        M = pl.eye(4)
        try:
            for dof, val in zip(cbone.dof, frame[node]):
                val = pl.deg2rad(val)
                R = pl.eye(4)
                if dof == 'rx':
                    R = Rx(val)
                elif dof == 'ry':
                    R = Ry(val)
                elif dof == 'rz':
                    R = Rz(val)

                M = pl.dot(R,M)
        except: #We might not have dof data for the current bone
            pass
        return M

    return { key: convert(key) for key in ['root'] + list(skeleton.bones.keys()) }

def animation_to_SO3(skeleton, animation):
    # Get rotation matrices for all joints and all frames
    bone_names = ['root'] + list(skeleton.bones.keys())

    frames = []
    for frame in animation.get_frames():
        frames.append(convert_to_SO3(skeleton, frame, True))
        
    # Convert into numpy arrays
    channels = pl.zeros((len(bone_names), len(frames), 3, 3))
    
    i = 0
    for key in animation.channel_order:
        if not key in bone_names:
            continue
        i += 1
        for j, frame in enumerate(frames):
            channels[i, j, :, :] = frame[key][:3,:3]

    for i in range(channels.shape[0]):
        for j in range(channels.shape[1]):
            if pl.array_equal(channels[i,j,:,:], pl.zeros((3,3))):
                channels[i, j, :, :] = pl.eye(3) 
            
    return channels
