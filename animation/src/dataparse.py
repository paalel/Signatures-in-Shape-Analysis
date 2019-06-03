from .animation import Animation
from .skeleton import Skeleton, Bone

import pylab as pl


def parse_array(lst):
    return pl.array( [float(x) for x in lst] )

def parse_amc(filename, description = "", remove_noisy_channels = True):
    data = []
    with open(filename,'r') as asf:
        data = asf.readlines()

    data = [line.strip() for line in data]  # Remove leading and trailing whitespace to simplify matters

    frames = []
    frame = None
    noisy_channels =  {'rtoes', 'ltoes', 'rthumb', 'lthumb', 'rfingers',
                       'lfingers', 'rhand', 'lhand'}

    for i, line in enumerate(data):
        #Skip to frames
        if line[0] in {':', '#'}:
            continue

        if line.isdigit():
            #Found a new frame
            if frame:
                frames.append(frame)
            frame = dict()
            continue

        tokens = line.split()

        if remove_noisy_channels and tokens[0] in noisy_channels:
            continue
        frame[tokens[0]] = parse_array(tokens[1:])

    return Animation(frames, description)

def parse_asf(filename, description = "", remove_noisy_channels = True):

    noisy_channels =  {'rtoes', 'ltoes', 'rthumb', 'lthumb', 'rfingers',
                       'lfingers', 'rhand', 'lhand'}
    data = []
    with open(filename,'r') as asf:
        data = asf.readlines()

    data = [line.strip() for line in data]  # Remove leading and trailing whitespace to simplify matters

    #---
    #Skip to bonedata
    bonedata = -1
    for i, line in enumerate(data):
        if line == ':bonedata':
            bonedata = i
            break

    if bonedata < 0:
        print('No bonedata found!')
        return

    bones = dict()
    bone = None
    end_bones = -1
    in_limits = False

    for i, line in enumerate(data[bonedata+1:]):
        tokens = line.split()

        #End of bonedata structure?
        if tokens[0][0] == ':':
            end_bones = i
            break

        #Begin of a single bone?
        if tokens[0] == 'begin':
            bone = Bone()

        #End of a single bone?
        if tokens[0] == 'end':
            if remove_noisy_channels and bone.name in noisy_channels:
                continue
            bones[bone.name] = bone

        #Bone data
        if tokens[0] == 'name':
            bone.name = tokens[1]

        if tokens[0] == 'direction':
            bone.direction = parse_array(tokens[1:4])

        if tokens[0] == 'length':
            bone.length = float(tokens[1])/0.45 * Skeleton.SCALE

        #TODO: Do I need to take the axis order into account for our data?
        if tokens[0] == 'axis':
            bone.axis = pl.deg2rad(parse_array(tokens[1:4]))

        if tokens[0] == 'dof':
            bone.dof = tokens[1:]

        #---
        #Axis limits
        #Assumes that "dof" was already set up
        if tokens[0] == 'limits':
            in_limits = True
            bone.limits.append((float(tokens[1][1:]), float(tokens[2][:-1])))
        elif in_limits:
            bone.limits.append((float(tokens[0][1:]), float(tokens[1][:-1])))
        if len(bone.limits) == len(bone.dof):
            in_limits = False


    #---
    #Skip to hierarchy
    hierarchy_index = -1
    for i, line in enumerate(data[bonedata+end_bones:]):
        if line == ':hierarchy':
            hierarchy_index = i
            break

    if hierarchy_index < 0:
        print('No hierarchy found!')
        return

    hierarchy_index += bonedata + end_bones

    skeleton = Skeleton(description)
    skeleton.bones = bones
    for line in data[hierarchy_index+1:]:
        tokens = line.split()

        #Begin of hierarchy?
        if tokens[0] == 'begin':
            continue

        #End of hierarchy?
        if tokens[0] == 'end':
            break

        skeleton.hierarchy[tokens[0]] = [c for c in tokens[1:] if c not in noisy_channels]

    return skeleton
