import os
import onnxruntime as ort
import pyaudio
import numpy as np
import threading

class WakeWordDetector:
    def __init__(self, model_path=None, callback=None,
                 threshold: float = 0.7,
                 rate: int = 16000, chunk: int = 512):
        """
        A simple ONNX-based wake word detector.
        model_path: path to .onnx file. If None, uses backend/model/marvin.onnx relative to this file.
        callback: function to call upon detection.
        """
        self.callback = callback
        self.threshold = threshold
        self.rate = rate
        self.chunk = chunk
        # Determine model path
        if model_path is None:
            base_dir = os.path.dirname(__file__)
            model_path = os.path.join(base_dir, 'model', 'marvin.onnx')
        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"ONNX model not found at {model_path}")
        # Initialize ONNX session
        try:
            self.session = ort.InferenceSession(model_path)
            self.input_name = self.session.get_inputs()[0].name
        except Exception as e:
            print(f"Warning: could not load ONNX model: {e} Wake-word detection disabled.")
            self.session = None
            self.input_name = None
        # Audio interface
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        self.running = False

    def run(self):
        """
        Start listening loop. Call callback when wake word detected.
        """
        if not self.session:
            return  # disabled if model load failed
        self.running = True
        while self.running:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            samples = np.frombuffer(data, dtype=np.int16).astype(np.float32)
            samples = samples / 32768.0  # normalize
            inp = samples.reshape(1, -1)
            scores = self.session.run(None, {self.input_name: inp})[0]
            if scores.size and scores[0][0] > self.threshold:
                if self.callback:
                    threading.Thread(target=self.callback, daemon=True).start()
        # cleanup
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def stop(self):
        """Stop the detection loop."""
        self.running = False