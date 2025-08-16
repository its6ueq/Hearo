import sys
import ctypes
import os
import queue

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QTimer, QLocale
from PySide6.QtGui import QIcon

from .core.transcription_engine import TranscriptionEngine
from .ui.main_window import ResizableOverlayWindow
from .core.text_processor import EnhancedTextProcessor
from .config.app_config import AppConfig

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
            self.engine = None
            self.is_running = False
            self.keyword_history = []
            
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
            """Initialize transcription engine with error handling"""
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
            <div class='loading'>
                <div class='spinner'></div>
                <p>Đang tải thông tin cho từ khóa '<span class="keyword">{keyword}</span>'...</p>
            </div>
            """
            self.main_window.update_ai_info(loading_html)

            info_html = self.text_processor.get_info_for_keyword(keyword)
            
            self.main_window.update_ai_info(info_html)

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
                    keywords_to_display = self.keyword_history[-MAX_KEYWORDS_TO_DISPLAY:]
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