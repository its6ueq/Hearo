
from faster_whisper import WhisperModel
import numpy as np
import torch

class Transcriber:
    def __init__(self, model_size, device, compute_type):
        print("Đang kiểm tra thiết bị...")
        if device.lower() == "cuda" and not torch.cuda.is_available():
            print("⚠ CUDA không khả dụng! Chuyển sang CPU...")
            device = "cpu"
            compute_type = "int8"
        
        print(f"Đang tải mô hình Whisper ({model_size}) trên {device}...")
        self.model = WhisperModel(
            model_size, 
            device=device, 
            compute_type=compute_type
        )
        print("✓ Tải mô hình thành công!")
        
        self.audio_buffer = np.array([], dtype=np.float32)

    def transcribe(self, new_audio_chunk, samplerate, required_length_seconds):
        if new_audio_chunk.ndim > 1:
            new_audio_chunk = new_audio_chunk.flatten()
            
        self.audio_buffer = np.concatenate([self.audio_buffer, new_audio_chunk])
        buffer_length_seconds = len(self.audio_buffer) / samplerate
        
        if buffer_length_seconds < required_length_seconds:
            return None
        
        print(f"Đã đủ {buffer_length_seconds:.2f}s âm thanh, đang phiên âm...")
        
        audio_energy = np.mean(np.abs(self.audio_buffer))
        print(f"Năng lượng trung bình của chunk âm thanh: {audio_energy:.6f}")
        
        if audio_energy < 0.01:
            print(f"⚠️  Âm thanh quá nhỏ ({audio_energy:.6f} < 0.01), bỏ qua...")
            self.audio_buffer = np.array([], dtype=np.float32)
            return None
        
        audio_to_transcribe = self.audio_buffer.copy()
        self.audio_buffer = np.array([], dtype=np.float32)

        segments, info = self.model.transcribe(
            audio_to_transcribe,
            beam_size=5,
            language=None,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )

        if info.language:
            print(f"Ngôn ngữ được phát hiện: {info.language} (tự tin: {info.language_probability:.2f})")

        transcribed_text = "".join(segment.text for segment in segments)
        
        if transcribed_text:
            print(f"Whisper đã phiên âm được: '{transcribed_text}'")
        else:
            print("Whisper đã xử lý nhưng không tìm thấy đoạn văn bản nào.")
            
        return transcribed_text.strip()