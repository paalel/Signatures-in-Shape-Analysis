from pylab import *

class Animation(object):
    def __init__(self, frames, description = ""):
        self._frames = frames
        self._description = description
        self._index = 0
        self._offset = zeros(3)
        self.channel_order = ['ltibia', 'root', 'lfoot', 'rthumb',
                'upperback', 'rfoot', 'head', 'rradius', 'lthumb', 'rfingers',
                'lhand', 'rfemur', 'lfemur', 'lradius',
                'lwrist', 'rtibia', 'lowerneck','thorax', 'lclavicle',
                'rclavicle', 'upperneck', 'rtoes', 'lowerback', 'rhumerus',
                'rhand', 'lfingers', 'lhumerus', 'rwrist']

    def move_root_to_origin(self):
        '''We want the center of our dummy to start in the origin.'''
        self._offset = -self._frames[0]['root'][0:3]

        for frame in self._frames:
            frame['root'][0:3] += self._offset

    def num_frames(self):
        return len(self._frames)

    def crop(self, start, end):
        self._frames = self._frames[start:end+1]

    def step(self, continuous = False):
        if not self._frames:
            return
        if self._index >= len(self._frames) - 1:
            self._index = 0
            if continuous:
                self._offset += self._frames[-1]['root'][0:3] - self._frames[0]['root'][0:3]
        else:
            self._index += 1

    def get_current_frame(self):
        if not self._frames or self._index < 0:
            return None

        return self._frames[self._index], self._offset

    def get_frame(self, index):
        return self._frames[index]

    def get_frames(self):
        return self._frames

    def set_frames(self, frames):
        self._frames = frames

    def get_channel_indices(self):
        channel_indices = dict()
        s = 0
        for c in self._frames[0].keys():
            channel_indices[c] = s
            s += self._frames[0][c].shape[0]

        return channel_indices


    def to_numpy_array(self):
        #Fetch curve data and stuff into a matrix
        channels = self._frames[0].keys()
        #Determine channel widths
        s = 0
        for c in channels:
            s += self._frames[0][c].shape[0]

        a = zeros((s, len(self._frames)))

        for i, frame in enumerate(self._frames):
            j = 0
            for c in channels:
                val = frame[c]
                w = val.shape[0]
                a[j : j + w, i] = val
                j += w

        return a

    def from_numpy_array(self, b):
        #Unpack matrix
        channels = self._frames[0].keys()
        sample_frame = self._frames[0]
        self._frames = []

        for i in range(b.shape[1]):
            frame = dict()
            j = 0
            for c in channels:
                w = sample_frame[c].shape[0]
                frame[c] = b[j : j + w, i]
                j += w
            self._frames.append(frame)
