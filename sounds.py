"""
class SoundIntrument():
    start_time=None

    def __init__(self):
        self.start_time=time.time()
"""


class PitchModifier(object):
    """
    Need to find a better way of changing pitch -> weird when more than 44000 samp/s
    """
    ratio = None

    # pitch modification ratio
    def __init__(self, ratio):
        super(PitchModifier, self).__init__()
        self.ratio = ratio

    def process(self, sound1, sound2=None):
        return sound1.set_samplerate(sound1.get_samplerate() * self.ratio)


class AddModifier(object):
    ratio = None

    # pitch modification ratio
    def __init__(self, ratio):
        super(AddModifier, self).__init__()
        self.ratio = ratio

    def process(self, sound1, sound2=None):
        return sound1.add(sound2, self.ratio)
