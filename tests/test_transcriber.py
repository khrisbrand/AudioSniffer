from src.transcriber import transcribe_audio

def test_transcription():
    text = transcribe_audio("audios/test.wav")
    assert isinstance(text, str)
