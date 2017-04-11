import sound_generator as sg
import subprocess
import threading
import time
import random

try:
    import ossaudiodev as ossa
    OSSAUDIO_AVAILABLE = True
except ImportError:
    print("ossaudiodev not found !")
try:
    import winaudio as wina
    WINAUDIO_AVAILABLE = True
except ImportError:
    print("winaudio not found !")


class SoundOutput():
    device = None
    # store the object to send the sound on
    type = None

    # 0: OSS, 1: WIN
    def __init__(self, device=None):
        if OSSAUDIO_AVAILABLE:
            self.type = 0
            devname = device
            if device is None:
                # finding device name
                (out, err) = subprocess.Popen(["ls /dev | grep dsp"], stdout=subprocess.PIPE, shell=True).communicate()
                devname = '/dev/' + out.decode("ascii")[:-1]
            # opening device
            dsp = None
            tries = 0
            while True:
                try:
                    tries += 1
                    dsp = ossa.open(devname, 'w')
                    break
                except Exception as e:
                    if tries >= 10:
                        print("Can't open device :", e)
                        break
                    else:
                        time.sleep(0.5)
            self.device = dsp
        elif WINAUDIO_AVAILABLE:
            self.type = 1
            print("Currently not supporting Windows")
        else:
            print("No modules found !")

    def play(self, sound):
        if self.type == 0:
            self.device.setparameters(ossa.AFMT_MPEG, sound.get_num_channels(), sound.get_samplerate())
            self.device.write(sound.get_data())
        elif self.type == 1:
            print("Currently not supporting Windows")
        else:
            print("Can't play sound !")

    def close(self):
        self.device.close()


class SoundPlayer(threading.Thread):
    is_running = None
    is_paused = None
    output = None
    last_sound = None
    # buffer to store the last played sound (play until new is received)
    to_be_played = None

    # list of sounds to be played (pop to last sound)
    def __init__(self):
        super(SoundPlayer, self).__init__()
        self.output = SoundOutput()
        self.is_running = True
        self.is_paused = True
        self.to_be_played = []
        self.daemon = True
        self.start()

    def play(self, sound):
        self.to_be_played.append(sound)
        self.is_paused = False

    def run(self):
        while self.is_running:
            if self.is_paused:
                time.sleep(0.01)
            else:
                if len(self.to_be_played) > 0:
                    self.last_sound = self.to_be_played.pop(0)
                self.output.play(self.last_sound)

    def kill(self, force=False):
        while not force and len(self.to_be_played) > 0:
            time.sleep(0.001)
        self.is_running = False
        self.output.close()
        self.join()

    def pause(self):
        self.is_paused = True


"""
mysound=sg.WaveGenerator().sinusoid(50)
mysound2=sg.WaveGenerator().progressiv(50)
mysound3=sg.WaveGenerator().progressiv(50,freqa=880,freqb=440)
(out, err) = subprocess.Popen(["ls /dev | grep dsp"], stdout=subprocess.PIPE, shell=True).communicate()
devname='/dev/'+out.decode("ascii")[:-1]
dsp=None
tries=0
while True:
    try:
        tries+=1
        dsp = ossa.open(devname,'w')
        break
    except:
        if tries>=10:
            break
while True:
    try:
        dsp.setparameters(ossa.AFMT_MPEG, 1, mysound.get_samplerate())
        dsp.write(mysound.get_data())
        dsp.setparameters(ossa.AFMT_MPEG, 1, mysound2.get_samplerate())
        dsp.write(mysound2.get_data())
        dsp.setparameters(ossa.AFMT_MPEG, 1, mysound3.get_samplerate())
        dsp.write(mysound3.get_data())
    except KeyboardInterrupt:
        break
dsp.close()
"""

player = SoundPlayer()
try:
    """
    while True:
        player.play(sg.WaveGenerator().sinusoid(50,freq=random.randint(20,20000)))
        time.sleep(0.05)
    """
    sound1 = sg.WaveGenerator().sinusoid(1000)
    sound2 = sg.WaveGenerator().sinusoid(1000, freq=500)
    sound3 = sg.WaveGenerator().sinusoid(1000, freq=550)
    player.play(sound1)
    player.play(sound2)
    player.play(sound3)
    player.play(sound1.add(sound2).add(sound3))
    player.kill(False)
except KeyboardInterrupt:
    pass
finally:
    player.kill(True)
