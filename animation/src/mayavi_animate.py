import mayavi.mlab as mlab
import pylab as pl
import traceback, sys

@mlab.show
@mlab.animate(delay=10, ui=True)
def mayavi_animate(skeleton, animation, offset, continuous=False, fixed_cam = False, frame_limit = -1, save_path = None):

    surf = mayavi_start_animation(skeleton)
    mlab.view(0,135, 25, pl.zeros(3), roll=0)
    f = mlab.gcf()
    while True:
        if animation._index > frame_limit > 0:
            return
        try:
            update_mayavi_surf_data(surf, skeleton, animation, offset)

            if not fixed_cam:
                mlab.view(30,35, 10, roll=0)

        except: # Exception,e:
            tb = traceback.format_exc()
            print(tb)
            return
        yield

def mayavi_start_animation(skeleton):
    lines = skeleton.get_skeleton_neutral_lines()
    coords = skeleton.get_skeleton_neutral_coords() 

    src = mlab.pipeline.scalar_scatter(coords[0], coords[1], coords[2])
    src.mlab_source.dataset.lines = skeleton._lines
    src.update()
    plotlines = mlab.pipeline.stripper(src)
    surf = mlab.pipeline.surface(plotlines, line_width=5.)
    return surf

def update_mayavi_surf_data(surf, skeleton, animation, offset):
    animation.step(animation)
    frame, anim_offset = animation.get_current_frame()
    coords = skeleton.get_coords_for_frame(frame, anim_offset)
    surf.mlab_source.reset(
        x = coords[0] + offset[0],
        y = coords[1] + offset[1],
        z = coords[2] + offset[2]
    )
