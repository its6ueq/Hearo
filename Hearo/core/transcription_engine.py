import soundcard as sc
import numpy as np
import threading
import time
import queue
from faster_whisper import WhisperModel
import torch

class TranscriptionEngine:
    def __init__(self, model_size="base", device="cuda", compute_type="float16", 
                 samplerate=16000, chunk_duration=3, text_queue=None):
        self.samplerate = samplerate
        self.chunk_duration = chunk_duration  # seconds
        self.audio_queue = queue.Queue()
        self.text_queue = text_queue or queue.Queue()
        self.is_running = False
        
        # Threads
        self.record_thread = None
        self.process_thread = None
        
        print("Khởi tạo Transcription Engine...")
        print("=" * 40)
        
        self.setup_audio()
        self.setup_model(model_size, device, compute_type)
    
    def setup_audio(self):
        """Setup audio device - Dựa trên logic từ run_terminal.py"""
        try:
            all_mics = sc.all_microphones(include_loopback=True)
            default_speaker = sc.default_speaker()
            
            # Find loopback device
            self.audio_device = None
            for mic in all_mics:
                if mic.isloopback and default_speaker.name in mic.name:
                    self.audio_device = mic
                    print(f"Using: {mic.name}")
                    break
            
            if not self.audio_device:
                # Fallback to stereo mix or any loopback
                for mic in all_mics:
                    if mic.isloopback or "stereo mix" in mic.name.lower():
                        self.audio_device = mic
                        print(f"Using fallback: {mic.name}")
                        break
            
            if not self.audio_device:
                raise Exception("No suitable audio device found")
                
        except Exception as e:
            print(f"Audio setup error: {e}")
            raise e
    
    def setup_model(self, model_size, device, compute_type):
        """Setup Whisper model"""
        # Auto-detect device như trong terminal version
        if device.lower() == "cuda" and not torch.cuda.is_available():
            print("CUDA không khả dụng! Chuyển sang CPU...")
            device = "cpu"
            compute_type = "int8"
        
        print(f"Loading WhisperModel ({model_size}) on {device.upper()}...")
        
        try:
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
            print("Model ready.")
        except Exception as e:
            print(f"Model loading error: {e}")
            raise e
    
    def record_loop(self):
        """Recording thread - Logic từ run_terminal.py"""
        try:
            with self.audio_device.recorder(samplerate=self.samplerate) as recorder:
                print("Bắt đầu ghi âm (loopback)...")
                
                while self.is_running:
                    # Record 0.1s chunks
                    chunk = recorder.record(numframes=int(self.samplerate * 0.1))
                    if chunk is not None:
                        # Convert to mono if stereo
                        if chunk.ndim > 1:
                            chunk = np.mean(chunk, axis=1)
                        self.audio_queue.put(chunk.astype(np.float32))
                        
        except Exception as e:
            print(f"Recording error: {e}")
            self.is_running = False
    
    def process_loop(self):
        """Processing thread - Logic từ run_terminal.py"""
        audio_buffer = np.array([], dtype=np.float32)
        chunk_size = self.samplerate * self.chunk_duration
        silence_counter = 0
        
        while self.is_running:
            try:
                # Collect audio
                while not self.audio_queue.empty():
                    chunk = self.audio_queue.get_nowait()
                    audio_buffer = np.concatenate([audio_buffer, chunk])
                
                # Check for silence every 0.1s worth of data
                if len(audio_buffer) >= int(self.samplerate * 0.1):
                    recent_chunk = audio_buffer[-int(self.samplerate * 0.1):]
                    energy = np.mean(np.abs(recent_chunk))
                    
                    if energy < 0.01:
                        silence_counter += 1
                        if silence_counter % 10 == 0:  # Every ~1 second
                            print(f"Im lặng: {silence_counter//10}s")
                    else:
                        if silence_counter > 5:
                            print(f"Âm thanh phát hiện! (energy: {energy:.4f})")
                        silence_counter = 0
                
                # Process when we have enough audio
                if len(audio_buffer) >= chunk_size:
                    # Take chunk and keep overlap
                    audio_chunk = audio_buffer[:int(chunk_size)].copy()
                    audio_buffer = audio_buffer[int(chunk_size//2):]  # 50% overlap
                    
                    # Check energy
                    avg_energy = np.mean(np.abs(audio_chunk))
                    
                    if avg_energy > 0.01:
                        print(f"Transcribing... (energy: {avg_energy:.4f})")
                        
                        # Transcribe
                        try:
                            segments, info = self.model.transcribe(
                                audio_chunk,
                                language="vi",  # Change to None for auto-detect
                                beam_size=5,
                                vad_filter=True,
                                task="transcribe"
                            )
                            
                            # Get text
                            text = "".join(segment.text for segment in segments).strip()
                            
                            if text:
                                timestamp = time.strftime('%H:%M:%S')
                                lang = getattr(info, 'language', 'unknown')
                                print("=" * 50)
                                print(f"{timestamp} | {lang} | {avg_energy:.4f}")
                                print(f"{text}")
                                print("=" * 50)
                                
                                # Gửi text qua queue cho UI
                                if self.text_queue:
                                    self.text_queue.put(text)
                            else:
                                print("Không phát hiện lời nói rõ ràng")
                                
                        except Exception as e:
                            print(f"Transcription error: {e}")
                    else:
                        print(f"Bỏ qua chunk yếu (energy: {avg_energy:.4f})")
                
                time.sleep(0.05)  # Small delay
                
            except Exception as e:
                print(f"Processing error: {e}")
                time.sleep(0.1)
    
    def start(self):
        """Start transcription"""
        if self.is_running:
            print("Engine đã đang chạy!")
            return
        
        print("Bắt đầu transcription engine...")
        self.is_running = True
        
        # Start threads
        self.record_thread = threading.Thread(target=self.record_loop, daemon=True)
        self.process_thread = threading.Thread(target=self.process_loop, daemon=True)
        
        self.record_thread.start()
        self.process_thread.start()
        
        print("Engine đã bắt đầu!")
    
    def stop(self):
        """Stop transcription"""
        if not self.is_running:
            print("Engine chưa chạy!")
            return
        
        print("Đang dừng engine...")
        self.is_running = False
        
        # Wait for threads to finish
        if self.record_thread and self.record_thread.is_alive():
            self.record_thread.join(timeout=2.0)
        
        if self.process_thread and self.process_thread.is_alive():
            self.process_thread.join(timeout=2.0)
        
        # Clear queues
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        print("Engine đã dừng!")
    
    def get_available_devices(self):
        """Trả về danh sách thiết bị âm thanh có sẵn"""
        try:
            all_mics = sc.all_microphones(include_loopback=True)
            devices = []
            for i, mic in enumerate(all_mics):
                device_type = "Loopback" if mic.isloopback else "🎤 Microphone"
                devices.append(f"{i}: {device_type} - {mic.name}")
            return devices
        except Exception as e:
            print(f"Error getting devices: {e}")
            return []
    
    def __del__(self):
        """Cleanup khi object bị destroy"""
        if self.is_running:
            self.stop()