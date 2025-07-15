import os
import time
import pyaudio
import numpy as np
from openwakeword.model import Model  # ✅ Use the high-level ONNX loader

class WakeWordListener:
    def __init__(self, on_detect):
        print("🟢 Aaron Assistant is listening...")

        # Load ONNX model manually
        model_path = os.path.join(os.path.dirname(__file__), "marvin.onnx")
        if not os.path.exists(model_path):
            raise FileNotFoundError("marvin.onnx not found in the project folder!")

        # ✅ Force ONNX backend only (avoid tflite)
        self.model = Model(
            backend="onnx",
            wakeword_models=[model_path]
        )

        self.on_detect = on_detect

        # Set up microphone stream
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=512
        )
        self.active = True

    def listen(self):
        print("🎙️ Listening for 'Aaron' wake word...")
        while self.active:
            audio = self.stream.read(512, exception_on_overflow=False)
            audio_data = np.frombuffer(audio, dtype=np.int16).astype(np.float32) / 32768.0

            result = self.model.predict(audio_data)
            if result.get("marvin", 0.0) > 0.7:
                print("🔔 Wake word 'Aaron' detected!")
                self.on_detect()
                time.sleep(2)  # brief pause to avoid retriggers
