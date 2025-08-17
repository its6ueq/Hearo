import sys
import ctypes
import os
import queue
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QTimer, QLocale, QThreadPool
from PySide6.QtGui import QIcon
from PySide6.QtCore import QThreadPool

from .core.transcription_engine import TranscriptionEngine
from .ui.main_window import ResizableOverlayWindow
from .core.text_processor import EnhancedTextProcessor
from .config.app_config import AppConfig
from .core.worker import Worker

def run_app():
    os.environ['QT_LOGGING_RULES'] = 'qt.widgets.style=false'
    app = QApplication(sys.argv)
    app.setApplicationName("LiveNote AI")
    app.setApplicationVersion("2.0")
    
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    try:
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.png')
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
    except Exception as e:
        print(f"Không thể tải icon: {e}")

    class ApplicationController:
        def __init__(self):
            self.threadpool = QThreadPool()
            self.engine = None
            self.is_running = False
            self.keyword_history = []
            self.active_workers = []
            
            print("Đang tải cấu hình...")
            self.config = AppConfig('config.ini')
            
            self.text_queue = queue.Queue()
            
            self.text_processor = EnhancedTextProcessor(config=self.config.text_processor)
        
            print("Khởi tạo giao diện...")
            self.main_window = ResizableOverlayWindow(
                start_callback=self.start_transcription,
                stop_callback=self.stop_transcription,
                keyword_callback=self.handle_keyword_click,
                config=self.config
            )
            
            print("Khởi tạo khu vực keywords rỗng...")
            self.main_window.set_keywords([])
            
            self.init_transcription_engine()
            
            self.queue_timer = QTimer()
            self.queue_timer.timeout.connect(self.check_transcription_queue)
            self.queue_timer.start(self.config.ui.queue_check_interval)
            
            app.aboutToQuit.connect(self.on_closing)
            
            self.main_window.show()
            print("Ứng dụng đã khởi tạo thành công!")

        def init_transcription_engine(self):
            try:
                print("Khởi tạo engine transcription...")
                self.engine = TranscriptionEngine(
                    model_size=self.config.whisper.model_size,
                    device=self.config.whisper.device,
                    compute_type=self.config.whisper.compute_type,
                    samplerate=self.config.audio.samplerate,
                    chunk_duration=self.config.audio.record_seconds,
                    text_queue=self.text_queue
                )
                print("Engine transcription đã sẵn sàng")
            except Exception as e:
                error_msg = f"Lỗi khởi tạo engine: {str(e)}"
                print(error_msg)
                self.main_window.text_display.setPlainText(f"Engine Error:\n{e}")
                self.main_window.start_button.setEnabled(False)

        def start_transcription(self):
            if not self.engine: return
            try:
                print("Bắt đầu transcription...")
                self.main_window.clear_all()
                self.text_processor.clear()
                self.engine.start()
                self.main_window.enable_stop_button()
                self.is_running = True
            except Exception as e:
                print(f"Lỗi bắt đầu transcription: {e}")

        def stop_transcription(self):
            if not self.engine: return
            print("Dừng transcription...")
            self.engine.stop()
            self.main_window.enable_start_button()
            self.is_running = False

        def handle_keyword_click(self, keyword):
            print(f"Yêu cầu thông tin cho từ khóa: {keyword}")

            loading_html = f"""
            <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; font-family: Segoe UI, sans-serif; color: #DCDDDE;'>
                <style>
                    .spinner {{
                        border: 4px solid rgba(255, 255, 255, 0.2);
                        border-left-color: #5865F2;
                        border-radius: 50%;
                        width: 40px;
                        height: 40px;
                        animation: spin 1s linear infinite;
                    }}
                    @keyframes spin {{
                        to {{ transform: rotate(360deg); }}
                    }}
                </style>
                <div class='spinner'></div>
                <p style='margin-top: 15px;'>Loading information for '<b>{keyword}</b>'...</p>
            </div>
            """
            self.main_window.update_ai_info(loading_html) 


            worker = Worker(self.text_processor.get_info_for_keyword, keyword)
            def cleanup_worker():
                if worker in self.active_workers:
                    self.active_workers.remove(worker)
                    
            worker.signals.result.connect(self.on_keyword_info_received)
            worker.signals.error.connect(self.on_keyword_info_error)
            worker.signals.finished.connect(cleanup_worker)

            self.active_workers.append(worker)
            self.threadpool.start(worker)
        
        def on_keyword_info_received(self, info_html):
            print(f" Dữ liệu nhận được (50 ký tự đầu): {info_html[:50]}")
            self.main_window.update_ai_info(info_html)

        def on_keyword_info_error(self, error_tuple):
            """Slot này sẽ được gọi khi worker gặp lỗi"""
            print(f"Lỗi khi lấy thông tin keyword: {error_tuple[0]} - {error_tuple[1]}")
            print(error_tuple[2]) 
            error_html = "<p style='color: #ED4245;'>Đã xảy ra lỗi khi tải thông tin. Vui lòng thử lại.</p>"
            self.main_window.update_ai_info(error_html)

        def check_transcription_queue(self):
            try:
                new_text_received = False
                new_keywords_generated = False
                
                while not self.text_queue.empty():
                    raw_text = self.text_queue.get_nowait()
                    processed_text, is_new = self.text_processor.process_text(raw_text)
                    if is_new:
                        new_text_received = True

                if new_text_received:
                    latest_sentences = self.text_processor.get_latest_sentences(2)
                    self.main_window.update_transcribed_text("\n\n".join(latest_sentences))
                    
                    last_sentence_list = self.text_processor.get_latest_sentences(1)
                    if last_sentence_list:
                        new_words = self.text_processor.extract_keywords_from_text(last_sentence_list[0])
                        if new_words:
                            self.keyword_history.extend(new_words)
                            new_keywords_generated = True

                if new_keywords_generated:
                    MAX_KEYWORDS_TO_DISPLAY = 15
                    keywords_to_display = self.keyword_history[-MAX_KEYWORDS_TO_DISPLAY:][::-1]
                    self.main_window.set_keywords(keywords_to_display)

            except queue.Empty:
                pass
            except Exception as e:
                print(f"Lỗi xử lý queue: {e}")
                
        def on_closing(self):
            print("Đang đóng ứng dụng...")
            if self.engine and self.is_running:
                self.stop_transcription()
            if self.config and self.config.ui.remember_position:
                geo = self.main_window.geometry()
                self.config.save_window_geometry(geo.x(), geo.y(), geo.width(), geo.height())
            print("Tạm biệt!")

    try:
        controller = ApplicationController()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Lỗi nghiêm trọng: {e}")
        with open("error.log", "w") as f:
            import traceback
            f.write(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    run_app()