import soundcard as sc
import numpy as np
import queue
import threading

class AudioProcessor:
    def __init__(self, samplerate, blocksize):
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.mics = sc.all_microphones(include_loopback=True)
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.recorder = None
        self.record_thread = None

    def get_devices(self):
        return self.mics

    def start_recording(self, device_index):
        device = self.mics[device_index]
        print(f"Bắt đầu ghi âm từ: {device.name}")
        
        self.recorder = device.recorder(
            samplerate=self.samplerate, 
            blocksize=self.blocksize
        )
        self.recorder.__enter__()
        
        self.is_recording = True
        self.record_thread = threading.Thread(target=self._record_audio)
        self.record_thread.daemon = True
        self.record_thread.start()

    def _record_audio(self):
        while self.is_recording:
            try:
                data = self.recorder.record(numframes=self.blocksize)
                if data is not None:
                    self.audio_queue.put(data)
            except Exception as e:
                print(f"Lỗi trong vòng lặp ghi âm: {e}")
                self.is_recording = False

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            
            if self.record_thread and self.record_thread.is_alive():
                self.record_thread.join(timeout=1.0)
            
            if self.recorder:
                self.recorder.__exit__(None, None, None)
                self.recorder = None
            
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except queue.Empty:
                    break

    def get_audio_data(self):
        try:
            return self.audio_queue.get_nowait()
        except queue.Empty:
            return None