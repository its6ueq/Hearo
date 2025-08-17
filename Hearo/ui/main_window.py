import sys
import qtawesome as qta
from PySide6.QtCore import Qt, QPoint, QTimer, QSize, QPropertyAnimation, QEasingCurve, QRect, Signal, QUrl, QObject, QRunnable, Slot
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
                               QHBoxLayout, QScrollArea, QFrame, QSplitter, QTextEdit,
                               QSizeGrip, QSizePolicy, QLayout, QGraphicsDropShadowEffect)
from PySide6.QtGui import QMouseEvent, QIcon, QFont, QPainter, QPen, QBrush, QColor, QPixmap
from PySide6.QtWebEngineWidgets import QWebEngineView

from ..styles.main_styles import UIStyles, WebViewStyles

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.
    Supported signals are:
    
    finished
        No data
    
    error
        `tuple` (exctype, value, traceback.format_exc())
    
    result
        `object` data returned from processing, anything
    '''
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)

class Worker(QRunnable):
    '''
    Worker thread
    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    '''
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            # Xử lý lỗi nếu có
            import traceback
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Trả về kết quả
        finally:
            self.signals.finished.emit()  # Báo cáo đã hoàn thành
            
class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=-1, spacing=-1):
        super().__init__(parent)
        if parent is not None: 
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.itemList = []
        
    def __del__(self):
        item = self.takeAt(0)
        while item: 
            item = self.takeAt(0)
            
    def addItem(self, item): 
        self.itemList.append(item)
        
    def count(self): 
        return len(self.itemList)
        
    def itemAt(self, index):
        if 0 <= index < len(self.itemList): 
            return self.itemList[index]
        return None
        
    def takeAt(self, index):
        if 0 <= index < len(self.itemList): 
            return self.itemList.pop(index)
        return None
        
    def expandingDirections(self): 
        return Qt.Orientation(0)
        
    def hasHeightForWidth(self): 
        return True
        
    def heightForWidth(self, width): 
        return self._do_layout(QRect(0, 0, width, 0), True)
        
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)
        
    def sizeHint(self): 
        return self.minimumSize()
        
    def minimumSize(self):
        size = QSize()
        for item in self.itemList: 
            size = size.expandedTo(item.minimumSize())
        margin, _, _, _ = self.getContentsMargins()
        size += QSize(2 * margin, 2 * margin)
        return size
        
    def _do_layout(self, rect, test_only):
        x, y, line_height = rect.x(), rect.y(), 0
        spacing = self.spacing()
        for item in self.itemList:
            wid = item.widget()
            space_x = spacing if spacing != -1 else wid.style().layoutSpacing(
                QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Horizontal)
            space_y = spacing if spacing != -1 else wid.style().layoutSpacing(
                QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Vertical)
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x, y, line_height = rect.x(), y + line_height + space_y, 0
                next_x = x + item.sizeHint().width() + space_x
            if not test_only: 
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        return y + line_height - rect.y()

class ModernButton(QPushButton):
    def __init__(self, text="", icon=None, button_type="default", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.is_hovered = False
        
        if icon:
            self.setIcon(icon)
            
        self.setFixedHeight(32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setup_style()
        
    def setup_style(self):
        styles = {
            "primary": {
                "bg": "#5865F2",
                "bg_hover": "#4752C4",
                "text": "#FFFFFF"
            },
            "secondary": {
                "bg": "#4F545C",
                "bg_hover": "#5D6269",
                "text": "#FFFFFF"
            },
            "success": {
                "bg": "#3BA55D",
                "bg_hover": "#2D7D32",
                "text": "#FFFFFF"
            },
            "danger": {
                "bg": "#ED4245",
                "bg_hover": "#C62828",
                "text": "#FFFFFF"
            },
            "default": {
                "bg": "#40444B",
                "bg_hover": "#484B51",
                "text": "#DCDDDE"
            }
        }
        
        style = styles.get(self.button_type, styles["default"])
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {style['bg']};
                color: {style['text']};
                border: none;
                border-radius: 6px;
                font-weight: 500;
                font-size: 14px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {style['bg_hover']};
            }}
            QPushButton:pressed {{
                background-color: {style['bg']};
                transform: scale(0.98);
            }}
            QPushButton:disabled {{
                background-color: #2F3136;
                color: #72767D;
            }}
        """)

class KeywordButton(ModernButton):
    keyword_clicked = Signal(str)
    
    def __init__(self, keyword, parent=None):
        # Không cần gọi super() của ModernButton vì chúng ta sẽ ghi đè style
        QPushButton.__init__(self, keyword, parent)
        self.keyword = keyword
        self.setFixedHeight(28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(lambda: self.keyword_clicked.emit(self.keyword))
        
        # Style mới - khớp với hình ảnh gốc
        self.setStyleSheet("""
            QPushButton {
                background-color: #5865F2; /* Màu xanh tím của Discord */
                color: #FFFFFF;
                border: none;
                border-radius: 14px; /* Bo tròn mạnh hơn */
                font-weight: 500;
                font-size: 12px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #4752C4; /* Sẫm hơn một chút khi hover */
            }
            QPushButton:pressed {
                background-color: #3C45A3; /* Sẫm hơn nữa khi nhấn */
            }
        """)

class ModernTextEdit(QTextEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setup_style()
        
    def setup_style(self):
        self.setStyleSheet("""
            QTextEdit {
                background-color: #2F3136;
                color: #DCDDDE;
                border: 2px solid #40444B;
                border-radius: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                line-height: 1.4;
                padding: 8px;
                selection-background-color: #5865F2;
            }
            QTextEdit:focus {
                border-color: #5865F2;
                outline: none;
            }
            QScrollBar:vertical {
                background-color: #2F3136;
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #5865F2;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4752C4;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

class ModernWebView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_link_handling()
        # Style sẽ được áp dụng từ file main_styles.py thông qua objectName
        self.setObjectName("infoWebView")
        self.page().setBackgroundColor(Qt.GlobalColor.transparent)

    def setup_link_handling(self):
        # Hàm này bắt các yêu cầu điều hướng (như click vào link)
        page = self.page()
        original_accept = page.acceptNavigationRequest
        
        def handle_navigation_request(url, nav_type, is_main_frame):
            # Nếu hành động là bấm vào một link
            if nav_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
                # Dùng QDesktopServices để mở link bằng trình duyệt mặc định của hệ thống
                QDesktopServices.openUrl(url)
                return False  # Ngăn WebView tự điều hướng bên trong
            
            # Cho phép các hành động khác (như tải trang ban đầu)
            return original_accept(url, nav_type, is_main_frame)
        
        page.acceptNavigationRequest = handle_navigation_request

class ModernScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_style()
        
    def setup_style(self):
        self.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
                border-radius: 8px;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2F3136;
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #5865F2;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4752C4;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                height: 0px;
            }
        """)

class ResizableOverlayWindow(QWidget):
    def __init__(self, start_callback, stop_callback, keyword_callback=None, config=None):
        super().__init__()
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.keyword_callback = keyword_callback
        self.config = config
        self.display_lines = []
        self.keywords = []

        # Configuration
        self.min_width = getattr(config.ui, 'min_width', 320) if config else 320
        self.max_width = getattr(config.ui, 'max_width', 600) if config else 600
        self.min_height = getattr(config.ui, 'min_height', 120) if config else 120
        self.expanded_height = getattr(config.ui, 'expanded_height', 500) if config else 500

        # Window setup
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setMinimumSize(self.min_width, self.min_height)
        self.setMaximumSize(self.max_width, self.expanded_height + 200)

        self._init_ui()
        self.position_window()
        self._drag_pos = QPoint()
        
        # Animation setup
        animation_duration = getattr(config.ui, 'animation_duration', 300) if config else 300
        self.resize_animation = QPropertyAnimation(self, b"geometry")
        self.resize_animation.setDuration(animation_duration)
        self.resize_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def _init_ui(self):
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main container with shadow effect
        self.main_container = QFrame()
        self.main_container.setObjectName("mainContainer")
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.main_container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(16, 12, 16, 16)
        container_layout.setSpacing(12)

        self._create_header(container_layout)
        self._create_sections()
        
        # Setup splitter
        self._setup_splitter(container_layout)
        
        self.main_layout.addWidget(self.main_container)
        
        # Size grip
        self.size_grip = QSizeGrip(self)
        
        self.apply_modern_stylesheet()
        self.enable_start_button()
    
    def _create_header(self, parent_layout):
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        # Title with icon
        title_container = QHBoxLayout()
        title_container.setSpacing(8)
        
        # App icon
        self.app_icon = QLabel("🎧")
        self.app_icon.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #5865F2;
            }
        """)
        
        self.title_label = QLabel("Hearo")
        self.title_label.setObjectName("title")
        self.title_label.setCursor(Qt.CursorShape.SizeAllCursor)
        
        title_container.addWidget(self.app_icon)
        title_container.addWidget(self.title_label)
        title_container.addStretch()
        
        # Control buttons
        self.expand_btn = ModernButton("", qta.icon('fa5s.compress-arrows-alt', color='#DCDDDE'), "default")
        self.expand_btn.setFixedSize(28, 28)
        self.expand_btn.clicked.connect(self.toggle_expansion)
        
        self.start_button = ModernButton("", qta.icon('fa5s.play', color='#FFFFFF'), "success")
        self.start_button.setFixedSize(32, 32)
        self.start_button.clicked.connect(self.on_start_click)
        
        self.stop_button = ModernButton("", qta.icon('fa5s.stop', color='#FFFFFF'), "danger")
        self.stop_button.setFixedSize(32, 32)
        self.stop_button.clicked.connect(self.on_stop_click)
        
        self.quit_button = ModernButton("", qta.icon('fa5s.times', color='#FFFFFF'), "danger")
        self.quit_button.setFixedSize(28, 28)
        self.quit_button.clicked.connect(QApplication.instance().quit)
        
        header_layout.addLayout(title_container)
        header_layout.addWidget(self.expand_btn)
        header_layout.addWidget(self.start_button)
        header_layout.addWidget(self.stop_button)
        header_layout.addWidget(self.quit_button)
        
        parent_layout.addLayout(header_layout)

    def _create_sections(self):
        # Text section
        self.text_section_widget = self._create_section_widget(
            "textSection", "📝 Live Transcription"
        )
        self.text_display = ModernTextEdit("Press ▶ to start listening...")
        self.text_display.setObjectName("textDisplay") # <-- THÊM DÒNG NÀY
        self.text_display.setReadOnly(True)
        self.text_section_widget.layout().addWidget(self.text_display)

        # Keywords section
        # DÁN KHỐI CODE NÀY VÀO THAY THẾ
        # Keywords section
        self.keywords_section_widget = self._create_section_widget(
            "keywordsSection", "🔖 Keywords"
        )
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("keywordsScroll")
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Widget container chính, sẽ được scroll area quản lý kích thước
        main_container = QWidget()

        # 1. Dùng một QVBoxLayout để ràng buộc chiều rộng và thêm margins
        v_layout = QVBoxLayout(main_container)

        # 2. Thêm khoảng cách lề: setContentsMargins(trái, trên, phải, dưới)
        #    Thêm 8px lề trái và 4px lề trên.
        v_layout.setContentsMargins(4, 4, 4, 4)
        v_layout.setSpacing(0)

        # Widget chứa FlowLayout (để FlowLayout không áp dụng trực tiếp lên container chính)
        flow_widget = QWidget()

        # 3. Khởi tạo FlowLayout, có thể giữ spacing cũ hoặc điều chỉnh nếu muốn
        self.keywords_layout = FlowLayout(flow_widget, margin=0, spacing=8) 

        # Thêm widget chứa FlowLayout vào layout dọc
        v_layout.addWidget(flow_widget)
        v_layout.addStretch(1) # Đảm bảo các keyword dồn lên trên

        scroll_area.setWidget(main_container)
        self.keywords_section_widget.layout().addWidget(scroll_area)

        # Info section
        self.info_section_widget = self._create_section_widget(
            "infoSection", "🤖 AI Information"
        )
        self.info_webview = ModernWebView()
        self.info_webview.setObjectName("infoWebView")
        self.info_webview.page().setBackgroundColor(Qt.GlobalColor.transparent)
        
        self.info_section_widget.layout().addWidget(self.info_webview, 1)

    def _create_section_widget(self, object_name, title):
        section_widget = QFrame()
        section_widget.setObjectName(object_name)
        
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(8)
        
        # Section title
        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        section_layout.addWidget(title_label)
        
        return section_widget
    
    def _setup_splitter(self, container_layout):
        # Inner splitter for keywords and info
        inner_splitter = QSplitter(Qt.Orientation.Vertical)
        inner_splitter.setChildrenCollapsible(False)
        inner_splitter.addWidget(self.keywords_section_widget)
        inner_splitter.addWidget(self.info_section_widget)
        inner_splitter.setSizes([100, 200])
        inner_splitter.setStretchFactor(1, 1)

        # Main splitter
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.addWidget(self.text_section_widget)
        self.splitter.addWidget(inner_splitter)
        self.splitter.setSizes([100, 300])
        self.splitter.setStretchFactor(1, 3)
        
        container_layout.addWidget(self.splitter)
    
    def apply_modern_stylesheet(self):
        # Use existing UIStyles with modern enhancements
        existing_styles = UIStyles.get_combined_stylesheet()
        
        # Add modern Discord-like enhancements while preserving original design
        modern_enhancements = """
            /* Enhanced main container with better gradient */
            #mainContainer {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(40, 44, 52, 0.95),
                    stop:1 rgba(30, 33, 36, 0.95));
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 15px;
            }
            
            /* Enhanced section titles */
            #sectionTitle {
                color: #1E88E5; 
                font-weight: 600;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin: 0px 0px 8px 0px;
                padding: 0px;
            }
            
            /* Better hover effects for buttons */
            #expandBtn:hover, #controlBtn:hover {
                background: rgba(30, 136, 229, 0.3);
                border: 1px solid rgba(30, 136, 229, 0.5);
            }
            
            /* Enhanced text display */
            #textDisplay {
                background: rgba(0, 0, 0, 0.4);
                border-radius: 8px;
                color: #e0e1e2;
                font-family: 'Segoe UI', 'Consolas', 'Courier New', monospace;
                font-size: 14px;
                padding: 15px;
                border: 1px solid rgba(255, 255, 255, 0.08);
                line-height: 1.5;
            }
        """
        
        combined_styles = existing_styles + "\n" + modern_enhancements
        self.setStyleSheet(combined_styles)

    def _run_collapse_animation(self):
        header_height = 60  # Approximate header height
        keywords_height = 120  # Fixed keywords section height
        margins = 40  # Total margins
        
        target_height = header_height + keywords_height + margins
        target_height = max(target_height, self.min_height)
        
        current_geometry = self.geometry()
        target_geometry = QRect(
            current_geometry.x(), 
            current_geometry.y(), 
            current_geometry.width(), 
            target_height
        )
        
        self.resize_animation.setStartValue(current_geometry)
        self.resize_animation.setEndValue(target_geometry)
        self.resize_animation.start()

    def _run_expand_animation(self):
        current_geometry = self.geometry()
        target_geometry = QRect(
            current_geometry.x(), 
            current_geometry.y(), 
            current_geometry.width(), 
            self.expanded_height
        )
        
        self.resize_animation.setStartValue(current_geometry)
        self.resize_animation.setEndValue(target_geometry)
        self.resize_animation.start()

    def position_window(self):
        if hasattr(self.config, 'get_window_geometry') and self.config.ui.remember_position:
            saved_geo = self.config.get_window_geometry()
            if saved_geo:
                self.setGeometry(*saved_geo)
                return
        
        # Default positioning
        screen_geo = QApplication.primaryScreen().geometry()
        margin = 20
        default_width = getattr(self.config.ui, 'default_width', 400) if self.config else 400
        default_height = getattr(self.config.ui, 'default_height', 300) if self.config else 300
        
        self.setGeometry(
            screen_geo.width() - default_width - margin,
            margin,
            default_width,
            default_height
        )

    def add_keywords(self, keywords_list):
        # Clear existing keywords
        while self.keywords_layout.count():
            child = self.keywords_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not keywords_list:
            no_keyword_label = QLabel("No keywords extracted yet...")
            no_keyword_label.setStyleSheet("""
                QLabel {
                    color: #72767D;
                    font-style: italic;
                    font-size: 12px;
                    padding: 8px;
                    background-color: #2F3136;
                    border-radius: 6px;
                }
            """)
            self.keywords_layout.addWidget(no_keyword_label)
        else:
            for keyword in keywords_list:
                button = KeywordButton(keyword)
                button.keyword_clicked.connect(self.on_keyword_clicked)
                self.keywords_layout.addWidget(button)

    def toggle_expansion(self):
        is_expanded = self.height() > (self.min_height + self.expanded_height) / 2

        if is_expanded:
            # Collapse
            self.expand_btn.setIcon(qta.icon('fa5s.expand-arrows-alt', color='#DCDDDE'))
            self.text_section_widget.setVisible(False)
            self.info_section_widget.setVisible(False)
            self.keywords_section_widget.setVisible(True)
            QTimer.singleShot(0, self._run_collapse_animation)
        else:
            # Expand
            self.expand_btn.setIcon(qta.icon('fa5s.compress-arrows-alt', color='#DCDDDE'))
            self.text_section_widget.setVisible(True)
            self.info_section_widget.setVisible(True)
            QTimer.singleShot(0, self._run_expand_animation)

    def update_transcribed_text(self, text):
        self.display_lines.append(text)
        if len(self.display_lines) > 2:
            self.display_lines.pop(0)
        
        self.text_display.setPlainText("\n\n".join(self.display_lines))
        scrollbar = self.text_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_keyword_clicked(self, keyword):
        is_expanded = self.height() > (self.min_height + self.expanded_height) / 2
        if not is_expanded:
            self.toggle_expansion()

        self.update_ai_info("<div style='color: #DCDDDE; padding: 20px; text-align: center;'>Loading...</div>")
        if self.keyword_callback:
            self.keyword_callback(keyword)

    def update_ai_info(self, html_content):
    # Đoạn mã này bọc nội dung HTML của bạn bằng style và script xử lý click
        enhanced_wrapper = f"""
        <html>
        <head>
            {WebViewStyles.get_dark_theme_wrapper()}
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    // Tìm tất cả các thẻ <a> có thuộc tính href
                    var links = document.querySelectorAll('a[href]');
                    links.forEach(function(link) {{
                        link.style.cursor = 'pointer';
                        link.addEventListener('click', function(e) {{
                            e.preventDefault();
                            // Dòng này sẽ kích hoạt yêu cầu điều hướng
                            // để code Python ở trên có thể bắt được
                            window.location.href = link.href;
                        }});
                    }});
                    
                    // Xử lý tương tự cho ảnh, nếu bạn muốn bấm vào ảnh cũng mở ra trình duyệt
                    var images = document.querySelectorAll('img[src]');
                    images.forEach(function(img) {{
                        img.style.cursor = 'pointer';
                        img.title = 'Click to open image';
                        img.addEventListener('click', function(e) {{
                            e.preventDefault();
                            window.location.href = img.src;
                        }});
                    }});
                }});
            </script>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        self.info_webview.setHtml(enhanced_wrapper)
        

    def clear_all(self):
        self.display_lines = []
        self.keywords = []
        self.text_display.setPlainText("Press ▶ to start listening...")
        self.add_keywords([])
        self.update_ai_info("")

    def on_start_click(self):
        if self.start_callback:
            self.start_callback()
            
    def on_stop_click(self):
        if self.stop_callback:
            self.stop_callback()

    def enable_stop_button(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
    def enable_start_button(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'size_grip'):
            self.size_grip.move(
                self.width() - self.size_grip.width(),
                self.height() - self.size_grip.height()
            )

    def closeEvent(self, event):
        if self.config and hasattr(self.config, 'save_window_geometry') and self.config.ui.remember_position:
            geo = self.geometry()
            self.config.save_window_geometry(geo.x(), geo.y(), geo.width(), geo.height())
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.title_label.underMouse():
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event: QMouseEvent):
        if (event.buttons() == Qt.MouseButton.LeftButton and 
            hasattr(self, '_drag_pos') and self._drag_pos):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = None

    def set_keywords(self, keywords_list):
        self.keywords = keywords_list
        self.add_keywords(keywords_list)