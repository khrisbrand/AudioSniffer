from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                               QLabel, QFileDialog, QProgressBar, QComboBox, QLCDNumber)
import sys
import sounddevice as sd
import numpy as np
import wave
import threading
import time
import speech_recognition as sr


class AudioSnifferApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.audio_filename = ""
        self.recording = False
        self.paused = False
        self.samplerate = 44100
        self.language = "es-ES"
        self.frames = []
        self.start_time = None
        self.stream = None

    def init_ui(self):
        self.setWindowTitle("Audio Sniffer")
        self.setGeometry(100, 100, 400, 300)
        layout = QVBoxLayout()

        self.status_label = QLabel("Listo para grabar")
        layout.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.timer_display = QLCDNumber()
        layout.addWidget(self.timer_display)

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

        self.resume_button = QPushButton("Continuar")
        self.resume_button.clicked.connect(self.resume_recording)
        layout.addWidget(self.resume_button)

        self.stop_button = QPushButton("Parar")
        self.stop_button.clicked.connect(self.stop_recording)
        layout.addWidget(self.stop_button)

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
        self.paused = False
        self.frames = []
        self.start_time = time.time()
        self.stream = sd.InputStream(samplerate=self.samplerate, channels=2, dtype=np.int16, callback=self.callback)
        self.stream.start()
        threading.Thread(target=self.update_timer).start()

    def pause_recording(self):
        self.paused = True
        self.status_label.setText("Pausado")

    def resume_recording(self):
        if self.paused:
            self.status_label.setText("Grabando...")
            self.paused = False

    def stop_recording(self):
        self.recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
        self.status_label.setText("Grabación finalizada")
        self.save_audio()

    def callback(self, indata, frames, time, status):
        if self.recording and not self.paused:
            self.frames.append(indata.copy())

    def update_timer(self):
        while self.recording:
            elapsed_time = int(time.time() - self.start_time)
            self.timer_display.display(elapsed_time)
            time.sleep(1)

    def save_audio(self):
        if not self.audio_filename:
            self.audio_filename = QFileDialog.getSaveFileName(self, "Guardar archivo", "", "Audio Files (*.wav)")[0]
        if self.audio_filename:
            with wave.open(self.audio_filename, "wb") as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(self.samplerate)
                wf.writeframes(b"".join([frame.tobytes() for frame in self.frames]))
            self.status_label.setText(f"Audio guardado en: {self.audio_filename}")

    def select_save_location(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", "", "Audio Files (*.wav)")
        if filename:
            self.audio_filename = filename
            self.status_label.setText(f"Guardando en: {filename}")

    def start_transcription(self):
        self.progress.setValue(0)
        threading.Thread(target=self.transcribe_audio).start()

    def transcribe_audio(self):
        if not self.audio_filename:
            self.status_label.setText("No hay archivo de audio para transcribir")
            return
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(self.audio_filename) as source:
                audio_data = recognizer.record(source)
            self.progress.setValue(50)
            text = recognizer.recognize_google(audio_data, language=self.language)
            self.status_label.setText(f"Texto: {text}")
        except sr.UnknownValueError:
            self.status_label.setText("No se pudo entender el audio")
        except sr.RequestError:
            self.status_label.setText("Error en el servicio de reconocimiento")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

        self.progress.setValue(100)


def run_gui():
    app = QApplication(sys.argv)
    window = AudioSnifferApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()
