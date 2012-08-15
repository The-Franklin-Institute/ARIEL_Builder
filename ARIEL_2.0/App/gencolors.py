
import wavelen2rgb

w = wavelen2rgb.wavelen2rgb

def getWave(f):
    return 390 + f * 290.0

for n in range(100):
    print n/100.0, w(getWave(n/100.0))

    


