import pyaudio
import numpy as np
 
CHUNK = 2**10
RATE = 44100
 
p=pyaudio.PyAudio()
# stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,frames_per_buffer=CHUNK,input_device_index=2)
# 위에 코드의 디바이스 코드가 해당 pc에 적합하지 않아서 디바이스 부분을 제거함)
stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,frames_per_buffer=CHUNK)


while(True):
    data = np.fromstring(stream.read(CHUNK),dtype=np.int16)
    print(int(np.average(np.abs(data))))
 
stream.stop_stream()
stream.close()
p.terminate()
