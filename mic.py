import pyaudio

p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    print(f"Índice {i}: {dev['name']}, {'Entrada' if dev['maxInputChannels'] > 0 else 'Salida'}")
p.terminate()
