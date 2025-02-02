import sounddevice as sd
import numpy as np
import wave

def record_audio(filename="audios/captura.wav", duration=5, sample_rate=44100):
    print("Grabando...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.int16)
    sd.wait()  # Esperar a que termine la grabación
    print("Grabación finalizada.")

    # Guardar el audio en un archivo WAV
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # Tamaño de 16 bits
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())

    print(f"Audio guardado en {filename}")
