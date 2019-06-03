import sys
sys.path.append("../../")
from animation import fetch_animations, unpack
from animation import save_similarity, fetch_animation_id_set, check_already_calucated
from animation import save_signature_distance

from so3.convert import animation_to_SO3
import so3.curves as curves
import so3.transformations as tf
import so3.helpers as hp
import so3.signature as signature

import numpy as np
import time

def crop_curve_based_on_id(curve, id):
    #forward jump
    if id == 1503:
        return hp.crop_curve(curve, start=140, stop=400)
    if id == 1497:
        return hp.crop_curve(curve, start=140, stop=400)
    if id == 1638:
        return hp.crop_curve(curve, start=60)
    if id == 1649:
        return hp.crop_curve(curve, start=120)
    if id == 1627:
        return hp.crop_curve(curve, start=70, stop=330)
    if id == 1616:
        return hp.crop_curve(curve, start=70, stop=380)
    if id == 1489:
        return hp.crop_curve(curve, start=100)
    if id == 1493:
        return hp.crop_curve(curve, start=100)
    if id == 537:
        return hp.crop_curve(curve, stop=400)
    if id == 537:
        return hp.crop_curve(curve, stop=400)

    return curve


start_time = time.time()

#print("fetch animation id set")
#id_set = [2019, 2034, 2041, 2035, 2038,1497]
#id_set = fetch_animation_id_set(count = 100, subject_fkey=70) + id_set
id_set = [ 1489, 1491, 1493, 1496, 1497, 1500, 1501, 1502, 1503, 1516, 1521, 1523, 1525, 1528, 1529, 1534, 1537, 1542, 2019, 2034, 2041, 2035, 2038, 1638,1649,1627,1616, 427, 2012,537, 245]

max_frames = 420
min_frames = 130

size = len(id_set)

explored = {}
depth = 4

for i in range(1,2):
    a_id = id_set[i]

    if a_id in explored:
        sig_a = explored[a_id]
    else:
        a_s, a_a, a_d = unpack(fetch_animations(1, animation_id = a_id))
        cad_full = animation_to_SO3(a_s, a_a)
        cad = crop_curve_based_on_id(cad_full, a_id)
        cad = curves.move_origin_to_zero(cad)
        sig_a = signature.curve_signature(cad, depth)
        explored[a_id] = sig_a

    for j in range(i, size):
        b_id = id_set[j]

        if b_id in explored:
            sig_b = explored[b_id]
        else:
            b_s, b_a, b_d = unpack(fetch_animations(1, animation_id = b_id))
            cbd_full = animation_to_SO3(b_s, b_a)
            cbd = crop_curve_based_on_id(cbd_full, b_id)
            cbd = curves.move_origin_to_zero(cbd)
            sig_b = signature.curve_signature(cbd, depth)
            explored[b_id] = sig_b

        signature_distance = signature.metric(sig_a, sig_b)
        save_signature_distance(a_id, b_id, signature_distance)
        print("iteration: %d,%d. seconds elapsed: %.2fs." % (i,j,time.time() - start_time))
