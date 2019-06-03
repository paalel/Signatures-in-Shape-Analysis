import sys
sys.path.append("../../")
from animation import fetch_animations, unpack
from animation import save_similarity, fetch_animation_id_set, check_already_calucated

from so3.convert import animation_to_SO3
import so3.curves as curves
import so3.transformations as tf
from id_set import get_id_set, crop_curve_based_on_id


import multiprocessing as mp
import numpy as np
import time

start_time = time.time()
max_frames = 420
min_frames = 130
depth = 8
processes = 8

id_set = get_id_set()
size = len(id_set)

explored = {}

def similarity(a,b):
    return (curves.dynamic_distance(a, b, depth), curves.distance(a,b))

def explore(id):
    subject , animation, description = unpack(fetch_animations(1, animation_id = id))
    curve_full = animation_to_SO3(subject, animation)
    curve = crop_curve_based_on_id(curve_full, id)
    return curves.move_origin_to_zero(curve), curve.shape[1]

def worker(i, j):
    a_id = id_set[i]
    a, a_size = explored[a_id]
    b_id = id_set[j]
    b, b_size = explored[b_id]

    if a_id == b_id:
        dp_distance = 0.0
        distance = 0.0
    else:
        dp_distance, distance = similarity(a, b)

    num, num2 = save_similarity(a_id, b_id, distance, dp_distance, a_size, b_size)
    print("iteration: %d,%d. seconds elapsed: %.2fs." % (i,j,time.time() - start_time))
    return

for i in range(size):
    id = id_set[i]
    explored[id] = explore(id)
    print("explored: %d. seconds elapsed: %.2fs." % (i,time.time() - start_time))

pool = mp.Pool(processes = processes)
for i in range(size):
    for j in range(i, size):
        pool.apply_async(worker, args=(i,j))

pool.close()
pool.join()
