import soundcard as sc
import numpy as np
import queue
import threading
import time

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
        
def find_loopback_device(devices):
    for i, device in enumerate(devices):
        name_lower = device.name.lower()
        if 'loopback' in name_lower or 'stereo mix' in name_lower or 'what u hear' in name_lower:
            return i, device
    return -1, None

if __name__ == "__main__":
    SAMPLERATE = 48000 
    BLOCKSIZE = 1024  
    RECORD_SECONDS = 5  

    audio_processor = AudioProcessor(samplerate=SAMPLERATE, blocksize=BLOCKSIZE)
    
    all_devices = audio_processor.get_devices()
    print("Các thiết bị ghi âm có sẵn:")
    for i, dev in enumerate(all_devices):
        print(f"  {i}: {dev.name}")

    loopback_index, loopback_device = find_loopback_device(all_devices)

    if loopback_index == -1:
        print("\nKhông tìm thấy thiết bị ghi âm thanh hệ thống.")
        exit()

    print(f"\nĐã chọn thiết bị loopback: '{loopback_device.name}'")
    print("-" * 30)

    print(f"Chuẩn bị ghi âm thanh hệ thống trong {RECORD_SECONDS} giây...")
    print("Hãy bật một bản nhạc hoặc video ngay bây giờ!")
    time.sleep(2) 

    audio_processor.start_recording(loopback_index)

    recorded_data = []
    start_time = time.time()
    while time.time() - start_time < RECORD_SECONDS:
        data_block = audio_processor.get_audio_data()
        if data_block is not None:
            recorded_data.append(data_block)
        
        time.sleep(0.01)

    audio_processor.stop_recording()

    if not recorded_data:
        print("Không có dữ liệu âm thanh nào được ghi lại.")
    else:
        print("\nĐã ghi xong. Chuẩn bị phát lại...")
        full_audio_data = np.concatenate(recorded_data, axis=0)

        default_speaker = sc.default_speaker()
        print(f"Đang phát lại trên: {default_speaker.name}")
        
        default_speaker.play(full_audio_data, samplerate=SAMPLERATE)
        
        print("Phát lại hoàn tất.")