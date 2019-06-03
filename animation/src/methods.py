from .skeleton import *
from .animation import *


class TransitionAnimation(Animation):
    def __init__(self, anim1, anim2):
        super(TransitionAnimation,self).__init__(None)

        self.__anim1 = anim1
        self.__anim2 = anim2

    def num_frames(self):
        return self.__anim1.num_frames() + self.__anim2.num_frames()

    def crop(self, start, end):
        pass

    def step(self, continuous = False):
        if self._index >= self.num_frames() - 1:
            self._index = 0
            if continuous:
                #print('jump 2->1')
                self._offset += self.__anim2.get_frame(-1)['root'][0:3] - \
                    self.__anim2.get_frame(0)['root'][0:3]
            return
        elif self._index == self.__anim1.num_frames() and continuous:
            #print('jump 1->2')
            self._offset += self.__anim1.get_frame(-1)['root'][0:3] - \
                self.__anim1.get_frame(0)['root'][0:3]

        self._index += 1

    def get_current_frame(self):
        lanim1 = self.__anim1.num_frames()
        if self._index < lanim1:
            return self.__anim1.get_frame(self._index), self._offset
        else:
            return self.__anim2.get_frame(self._index - lanim1), self._offset

class CompositeAnimation(Animation):
    def __init__(self, animations):
        super(CompositeAnimation,self).__init__(
            reduce(lambda l, e: l + e._frames, animations, []))

        #Ok, now we've alreay combined all th frames.
        #We still need to adjust the global translation to have a continuous
        #motion throughout the whole composite animation
        for i, anim in enumerate(animations):
            offset = anim.get_frame(-1)['root'][0:3] - \
                anim.get_frame(0)['root'][0:3]

            #Add this offset to all subsequent animations
            for nanim in animations[i+1:]:
                for frame in nanim._frames:
                    frame['root'][0:3] += offset

class InterpolatedAnimation(Animation):
    def __init__(self, animations, weights):
        weighted_frames = []

        for i, weights in enumerate(weights):
            weighted_frames.append(dict())

            for key in animations[0]._frames[0].iterkeys():
                interp = animations[0]._frames[i][key] * weights[0]

                for j, anim in enumerate(animations[1:]):
                    interp += anim._frames[i][key] * weights[j+1]

                weighted_frames[i][key] = interp

        super(InterpolatedAnimation,self).__init__(weighted_frames)


class MatchedAnimation(Animation):
    def __init__(self, anim1, anim2, weights):
        super(MatchedAnimation,self).__init__(anim1._frames)
        #def match_animations(anim1, anim2, requests):
        a = anim1.to_numpy_array()
        b = anim2.to_numpy_array()

        #Match lengths
        from scipy.interpolate import interp1d
        interp = interp1d(linspace(0,1,b.shape[1],endpoint=True), b)
        c = interp(linspace(0,1,a.shape[1],endpoint=True))

        #Handle translation channels separately
        rindex = anim1.get_channel_indices()['root']
        transa = a[rindex:rindex+3].copy()
        transb = c[rindex:rindex+3].copy()
        a[rindex:rindex+3] = 0
        c[rindex:rindex+3] = 0

        l = matching.length(a)
        a /= l

        lc = matching.length(c)
        c /= lc

        ap = matching.dir_fct_from_curve(a)
        bp = matching.dir_fct_from_curve(c)

        path = matching.path_straightening(ap, bp, K=7, its = 2)

        #anims = []
        #for i in requests:
        d = path[3]
        t = 0.5
        #print(norm(a-b))
        #b *= l
        n = matching.curve_from_dir_fct(d, a[:,0])
        n *= l

        n[rindex:rindex+3] = t * transb + (1. - t) * transa

        self.from_numpy_array(n)

        #new_anim = Animation([di.copy() for di in anim1.get_frames()])

        #new_anim.from_numpy_array(n)
        #anims.append(new_anim)

        #return anims

