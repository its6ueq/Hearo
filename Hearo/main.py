import tkinter as tk
import configparser
import ctypes
import sys
import os
import queue

# Import engine mới
from .core.transcription_engine import TranscriptionEngine
from .ui.main_window import MainWindow

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except AttributeError:
        return False

def run_app():
    class Application:
        def __init__(self, root):
            self.root = root
            self.engine = None
            
            if not os.path.exists('config.ini'):
                self.create_default_config()
            
            self.config = configparser.ConfigParser()
            self.config.read('config.ini', encoding='utf-8')

            audio_config = self.config['Audio']
            whisper_config = self.config['Whisper']

            # Hàng đợi để giao tiếp giữa engine và giao diện
            self.text_queue = queue.Queue()

            # Khởi tạo UI trước
            self.main_window = MainWindow(
                self.root, 
                start_callback=self.start_transcription, 
                stop_callback=self.stop_transcription
            )

            try:
                # Khởi tạo động cơ phiên âm với logic mới
                self.engine = TranscriptionEngine(
                    model_size=whisper_config['model_size'],
                    device=whisper_config['device'],
                    compute_type=whisper_config['compute_type'],
                    samplerate=int(audio_config['samplerate']),
                    chunk_duration=int(audio_config['record_seconds']),
                    text_queue=self.text_queue
                )
                
                # Hiển thị thông tin thiết bị có sẵn
                devices = self.engine.get_available_devices()
                print("\n📋 Thiết bị âm thanh có sẵn:")
                for device in devices:
                    print(f"   {device}")
                print()
                    
            except Exception as e:
                print(f"FATAL: Không thể khởi tạo Transcription Engine: {e}")
                # Hiển thị lỗi trên UI
                error_msg = f"Lỗi khởi tạo engine: {str(e)}\nVui lòng kiểm tra cấu hình và thử lại."
                self.main_window.update_transcribed_text(error_msg)
                self.main_window.start_button.config(state=tk.DISABLED)
                return
            
            # Bắt đầu vòng lặp kiểm tra kết quả từ engine
            self.check_transcription_queue()

        def create_default_config(self):
            config = configparser.ConfigParser()
            config['Audio'] = {
                'samplerate': '16000', 
                'record_seconds': '3'
            }
            config['Whisper'] = {
                'model_size': 'base', 
                'device': 'cuda', 
                'compute_type': 'float16'
            }
            with open('config.ini', 'w', encoding='utf-8') as configfile:
                config.write(configfile)
            print("Đã tạo file config.ini mặc định")

        def start_transcription(self):
            if not self.engine:
                print("Engine chưa được khởi tạo!")
                return
                
            try:
                self.engine.start()
                self.main_window.enable_stop_button()
                print("Đã bắt đầu transcription")
            except Exception as e:
                print(f"Lỗi khi bắt đầu transcription: {e}")
                self.main_window.update_transcribed_text(f"Lỗi: {str(e)}\n")

        def stop_transcription(self):
            if not self.engine:
                print("Engine chưa được khởi tạo!")
                return
                
            try:
                self.engine.stop()
                self.main_window.enable_start_button()
                print("Đã dừng transcription")
            except Exception as e:
                print(f"Lỗi khi dừng transcription: {e}")

        def check_transcription_queue(self):
            """Kiểm tra hàng đợi và cập nhật UI một cách an toàn"""
            processed_items = 0
            
            try:
                while not self.text_queue.empty():
                    try:
                        text = self.text_queue.get_nowait()
                        processed_items += 1
                        print(f"UI nhận được ({processed_items}): '{text}'")
                        
                        # Thêm timestamp cho UI
                        import time
                        timestamp = time.strftime('%H:%M:%S')
                        formatted_text = f"[{timestamp}] {text}\n"
                        self.main_window.update_transcribed_text(formatted_text)
                        
                    except queue.Empty:
                        break
                        
            except Exception as e:
                print(f"Lỗi trong check_transcription_queue: {e}")
            
            # Debug: Hiển thị queue size nếu có
            queue_size = self.text_queue.qsize()
            if queue_size > 0:
                print(f"Còn {queue_size} items trong queue")
            
            # Lên lịch kiểm tra lại sau 100ms
            self.root.after(100, self.check_transcription_queue)
    
    root = tk.Tk()
    root.attributes('-topmost', True)  # Buộc cửa sổ luôn nổi lên trên
    app = Application(root)
    
    def on_closing():
        print("Đang đóng ứng dụng...")
        if app.engine and app.engine.is_running:
            app.stop_transcription()
        root.destroy()
        print("Goodbye!")
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    # Kiểm tra quyền admin nếu cần
    if not is_admin():
        print("Khuyến nghị chạy với quyền Administrator để truy cập đầy đủ thiết bị âm thanh")
    
    run_app()