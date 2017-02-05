import wave, os, math, pyaudio, sys,struct

"""
Offset  Size  Name             Description

The canonical WAVE format starts with the RIFF header:

0         4   ChunkID          Contains the letters "RIFF" in ASCII form
                               (0x52494646 big-endian form).
4         4   ChunkSize        36 + SubChunk2Size, or more precisely:
                               4 + (8 + SubChunk1Size) + (8 + SubChunk2Size)
                               This is the size of the rest of the chunk
                               following this number.  This is the size of the
                               entire file in bytes minus 8 bytes for the
                               two fields not included in this count:
                               ChunkID and ChunkSize.
8         4   Format           Contains the letters "WAVE"
                               (0x57415645 big-endian form).

The "WAVE" format consists of two subchunks: "fmt " and "data":
The "fmt " subchunk describes the sound data's format:

12        4   Subchunk1ID      Contains the letters "fmt "
                               (0x666d7420 big-endian form).
16        4   Subchunk1Size    16 for PCM.  This is the size of the
                               rest of the Subchunk which follows this number.
20        2   AudioFormat      PCM = 1 (i.e. Linear quantization)
                               Values other than 1 indicate some
                               form of compression.
22        2   NumChannels      Mono = 1, Stereo = 2, etc.
24        4   SampleRate       8000, 44100, etc.
28        4   ByteRate         == SampleRate * NumChannels * BitsPerSample/8
32        2   BlockAlign       == NumChannels * BitsPerSample/8
                               The number of bytes for one sample including
                               all channels. I wonder what happens when
                               this number isn't an integer?
34        2   BitsPerSample    8 bits = 8, 16 bits = 16, etc.
          2   ExtraParamSize   if PCM, then doesn't exist
          X   ExtraParams      space for extra parameters

The "data" subchunk contains the size of the data and the actual sound:

36        4   Subchunk2ID      Contains the letters "data"
                               (0x64617461 big-endian form).
40        4   Subchunk2Size    == NumSamples * NumChannels * BitsPerSample/8
                               This is the number of bytes in the data.
                               You can also think of this as the size
                               of the read of the subchunk following this
                               number.
44        *   Data             The actual sound data.
"""

class WaveSound(object):
    raw_data=b""
    length=0
    sample_rate=0
    bits_per_sample=0
    def __init__(self,sample_rate=22000,bits_per_sample=8):
        super().__init__()
        self.sample_rate=sample_rate
        self.bits_per_sample=bits_per_sample

    def add_value(self,val):
        assert type(val)==int
        self.raw_data+=val.to_bytes(int(self.get_bitpersample()/8),byteorder="big")
        self.length+=1
        return self

    def __add__(self, other):
        assert type(other)==WaveSound
        assert self.get_samplerate()==other.get_samplerate()
        return WaveSound(self.get_samplerate()).set_data(self.get_data()+other.get_data())

    def set_data(self,data):
        self.raw_data=data
        self.length=len(data)
        return self

    def get_samplerate(self):
        return self.sample_rate

    def get_bitpersample(self):
        return self.bits_per_sample

    def get_data(self):
        return self.raw_data

    def get_copy(self):
        return WaveSound(self.get_samplerate()).set_data(self.get_data())

    def get_length(self):
        return self.length

    def save(self,filename):
        wave_file = open(filename, 'wb')


        subchunk1_size=16 # (PCM)
        subchunk2_size=int(self.get_length() * self.get_bitpersample()/8)

        # RIFF Header
        wave_file.write(b"RIFF")
        wave_file.write((4 + (8 + subchunk1_size) + (8 + subchunk2_size)).to_bytes(4, byteorder='little'))
        wave_file.write(b"WAVE")

        # SubChunk1
        wave_file.write(b"fmt ")
        wave_file.write(subchunk1_size.to_bytes(4,byteorder="little"))
        wave_file.write((1).to_bytes(2,byteorder="little")) # (No compression)
        wave_file.write((1).to_bytes(2,byteorder="little")) # (Mono)
        wave_file.write(self.get_samplerate().to_bytes(4,byteorder="little")) # (Sample rate)
        wave_file.write(int(self.get_samplerate()*self.get_bitpersample()/8).to_bytes(4,byteorder="little")) # (Bit rate)
        wave_file.write(int(self.get_bitpersample()/8).to_bytes(2,byteorder="little")) # (Block align)
        wave_file.write(self.get_bitpersample().to_bytes(2,byteorder="little")) # (Bit per sample)

        # SubChunk2
        wave_file.write(b"data")
        wave_file.write(subchunk2_size.to_bytes(4,byteorder="little")) # (Bit per sample)
        wave_file.write(self.get_data())

        wave_file.close()
        return self

    def get_data_as_int_array(self):
        return [e for e in self.get_data()]

class WaveGenerator():
    def sinusoid(self,time=1000,sample_rate=22000,freq=440):
        sound=WaveSound(sample_rate)
        for i in range(int(time*sample_rate/1000)):
            v=math.sin(2 * math.pi * i * freq / sample_rate)*127+127
            sound.add_value(int(v))
        return sound

    def advanced_sinusoid(self,periods=100,sample_rate=22000,freq=440):
        sound=WaveSound(sample_rate)
        period=WaveSound(sample_rate)
        for i in range(int(sample_rate/freq)):
            v=math.sin(2 * math.pi * (i/(sample_rate/freq)))*127+127
            period.add_value(int(v))
        for i in range(periods):
            sound+=period
        return sound

    def progressiv(self,time=1000,sample_rate=22000,freqa=440,freqb=880):
        sound=WaveSound(sample_rate)
        n=int(time*sample_rate/1000)
        for i in range(n):
            v=math.sin(2 * math.pi * i * (freqa+(i*(freqb-freqa)/n)) / sample_rate)*127+127
            sound.add_value(int(v))
        return sound

"""
  ..        ..
.    .    .    .    .
       ..        ..
|         |
0         2pi
"""

v=WaveGenerator().sinusoid(sample_rate=44100,time=1000,freq=440)
v.save("hello.wav")

"""
dat=v.get_data_as_int_array()
print(dat)
from turtle import *
s=(340*2,280*2)
pen=Pen()
pen.penup()
pen.backward(s[0]/2)
l=len(dat)
for i in range(l):
    x=i*s[0]/(l-1)-s[0]/2
    normal=(dat[i]-127)/(255)
    pen.goto(x,normal*s[1])
    pen.pendown()
input()
"""#"""
