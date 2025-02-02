from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
import sys
from src.recorder import record_audio
from src.transcriber import transcribe_audio

class AudioSnifferApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Audio Sniffer")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.status_label = QLabel("Presiona para grabar audio del navegador")
        layout.addWidget(self.status_label)

        self.record_button = QPushButton("Grabar")
        self.record_button.clicked.connect(self.start_recording)
        layout.addWidget(self.record_button)

        self.transcribe_button = QPushButton("Transcribir")
        self.transcribe_button.clicked.connect(self.start_transcription)
        layout.addWidget(self.transcribe_button)

        self.setLayout(layout)

    def start_recording(self):
        self.status_label.setText("Grabando...")
        record_audio("audios/captura.wav")
        self.status_label.setText("Grabación guardada.")

    def start_transcription(self):
        text = transcribe_audio("audios/captura.wav")
        self.status_label.setText(f"Texto: {text}")

def run_gui():
    app = QApplication(sys.argv)
    window = AudioSnifferApp()
    window.show()
    sys.exit(app.exec())
