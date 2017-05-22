class DeviceValue(object):
    current_value=0
    def __init__(self):
        super(DeviceValue, self).__init__()

    def set_value(self,value):
        self.current_value=value

    def get_value(self):
        return self.current_value


class Modifier(object):
    device_values=None
    # array of 'DeviceValue'
    def __init__(self, device_values):
        super(Modifier, self).__init__()
        self.device_values=device_values

    def run(self, sounds):
        """
        :param sounds: sounds to be processed (array of 'WaveSound')
        :return: result sound
        """
        return self.process(sounds)

    def process(self,sounds):
        raise NotImplementedError()