import speech_recognition as sr

def transcribe_audio(filename="audios/captura.wav"):
    recognizer = sr.Recognizer()

    with sr.AudioFile(filename) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data, language="es-ES")
        print("Transcripción:", text)
        return text
    except sr.UnknownValueError:
        print("No se pudo entender el audio")
        return ""
    except sr.RequestError:
        print("Error en la solicitud a Google Speech Recognition")
        return ""
