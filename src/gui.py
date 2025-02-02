from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                               QLabel, QFileDialog, QProgressBar, QComboBox)
import sys
import sounddevice as sd
import numpy as np
import wave
import threading
import speech_recognition as sr


class AudioSnifferApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.audio_filename = ""
        self.recording = False
        self.samplerate = 44100
        self.language = "es-ES"

    def init_ui(self):
        self.setWindowTitle("Audio Sniffer")
        self.setGeometry(100, 100, 400, 300)
        layout = QVBoxLayout()

        self.status_label = QLabel("Listo para grabar")
        layout.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.language_select = QComboBox()
        self.language_select.addItems(["es-ES", "en-US", "fr-FR", "de-DE", "it-IT"])
        self.language_select.currentTextChanged.connect(self.change_language)
        layout.addWidget(self.language_select)

        self.record_button = QPushButton("Grabar")
        self.record_button.clicked.connect(self.start_recording)
        layout.addWidget(self.record_button)

        self.pause_button = QPushButton("Pausar")
        self.pause_button.clicked.connect(self.pause_recording)
        layout.addWidget(self.pause_button)

        self.play_button = QPushButton("Reproducir")
        self.play_button.clicked.connect(self.play_audio)
        layout.addWidget(self.play_button)

        self.save_button = QPushButton("Guardar en...")
        self.save_button.clicked.connect(self.select_save_location)
        layout.addWidget(self.save_button)

        self.transcribe_button = QPushButton("Transcribir")
        self.transcribe_button.clicked.connect(self.start_transcription)
        layout.addWidget(self.transcribe_button)

        self.setLayout(layout)

    def change_language(self, lang):
        self.language = lang

    def start_recording(self):
        self.status_label.setText("Grabando...")
        self.recording = True
        threading.Thread(target=self.record_audio).start()

    def pause_recording(self):
        self.recording = False
        self.status_label.setText("Pausado")

    def record_audio(self):
        duration = 5  # Se puede cambiar
        audio_data = sd.rec(int(duration * self.samplerate), samplerate=self.samplerate, channels=1, dtype=np.int16)
        sd.wait()
        self.progress.setValue(50)

        if self.audio_filename == "":
            self.audio_filename = "captura.wav"

        with wave.open(self.audio_filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.samplerate)
            wf.writeframes(audio_data.tobytes())

        self.progress.setValue(100)
        self.status_label.setText("Grabación guardada")

    def play_audio(self):
        if self.audio_filename:
            import simpleaudio as sa
            wave_obj = sa.WaveObject.from_wave_file(self.audio_filename)
            wave_obj.play()

    def select_save_location(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", "", "Audio Files (*.wav)")
        if filename:
            self.audio_filename = filename
            self.status_label.setText(f"Guardando en: {filename}")

    def start_transcription(self):
        self.progress.setValue(0)
        threading.Thread(target=self.transcribe_audio).start()

    def transcribe_audio(self):
        recognizer = sr.Recognizer()
        with sr.AudioFile(self.audio_filename) as source:
            audio_data = recognizer.record(source)
        self.progress.setValue(50)

        try:
            text = recognizer.recognize_google(audio_data, language=self.language)
            self.status_label.setText(f"Texto: {text}")
        except sr.UnknownValueError:
            self.status_label.setText("No se pudo entender el audio")
        except sr.RequestError:
            self.status_label.setText("Error en el servicio de reconocimiento")

        self.progress.setValue(100)


def run_gui():
    app = QApplication(sys.argv)
    window = AudioSnifferApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()
