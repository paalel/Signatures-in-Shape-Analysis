#!/usr/bin/python3
from animation.src.mayavi_animate import mayavi_animate
from animation import fetch_animations, unpack
import sys

#usage: ./display_animation.py YY XX

print("Load data")
file_name = sys.argv[1] + "_" + sys.argv[2] + ".amc"
data = fetch_animations(1, file_name = file_name)
if not data:
    print("No animations found.")
    sys.exit()

print("Parse data")
s, a, d = unpack(data)

print("Run animation")
mayavi_animate(s, a, [0,0,0])
print("description: " + d)
print("animation shape:", a.num_frames())

