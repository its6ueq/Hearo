import sys
import qtawesome as qta
from PySide6.QtCore import Qt, QPoint, QTimer, QSize, QPropertyAnimation, QEasingCurve, QRect, Signal
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
                               QHBoxLayout, QScrollArea, QFrame, QSplitter, QTextEdit,
                               QSizeGrip, QSizePolicy, QLayout)
from PySide6.QtGui import QMouseEvent, QIcon, QFont
from PySide6.QtWebEngineWidgets import QWebEngineView

from ..styles.main_styles import UIStyles, WebViewStyles

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=-1, spacing=-1):
        super().__init__(parent)
        if parent is not None: self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.itemList = []
    def __del__(self):
        item = self.takeAt(0)
        while item: item = self.takeAt(0)
    def addItem(self, item): self.itemList.append(item)
    def count(self): return len(self.itemList)
    def itemAt(self, index):
        if 0 <= index < len(self.itemList): return self.itemList[index]
        return None
    def takeAt(self, index):
        if 0 <= index < len(self.itemList): return self.itemList.pop(index)
        return None
    def expandingDirections(self): return Qt.Orientation(0)
    def hasHeightForWidth(self): return True
    def heightForWidth(self, width): return self._do_layout(QRect(0, 0, width, 0), True)
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)
    def sizeHint(self): return self.minimumSize()
    def minimumSize(self):
        size = QSize()
        for item in self.itemList: size = size.expandedTo(item.minimumSize())
        margin, _, _, _ = self.getContentsMargins()
        size += QSize(2 * margin, 2 * margin)
        return size
    def _do_layout(self, rect, test_only):
        x, y, line_height = rect.x(), rect.y(), 0
        spacing = self.spacing()
        for item in self.itemList:
            wid = item.widget()
            space_x = spacing if spacing != -1 else wid.style().layoutSpacing(QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Horizontal)
            space_y = spacing if spacing != -1 else wid.style().layoutSpacing(QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Vertical)
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x, y, line_height = rect.x(), y + line_height + space_y, 0
                next_x = x + item.sizeHint().width() + space_x
            if not test_only: item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        return y + line_height - rect.y()

class KeywordButton(QPushButton):
    keyword_clicked = Signal(str)
    def __init__(self, keyword, parent=None):
        super().__init__(keyword, parent)
        self.keyword = keyword
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(lambda: self.keyword_clicked.emit(self.keyword))

class ResizableOverlayWindow(QWidget):
    def __init__(self, start_callback, stop_callback, keyword_callback=None, config=None):
        super().__init__()
        self.start_callback, self.stop_callback, self.keyword_callback = start_callback, stop_callback, keyword_callback
        self.config = config
        self.display_lines, self.keywords = [], []

        self.min_width = config.ui.min_width
        self.max_width = config.ui.max_width
        self.min_height = config.ui.min_height
        self.expanded_height = config.ui.expanded_height

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setMinimumSize(self.min_width, self.min_height)
        self.setMaximumSize(self.max_width, self.expanded_height + 200)

        self._init_ui()
        self.position_window()
        self._drag_pos = QPoint()
        
        self.resize_animation = QPropertyAnimation(self, b"geometry")
        self.resize_animation.setDuration(config.ui.animation_duration)
        self.resize_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.main_container = QFrame()
        self.main_container.setObjectName("mainContainer")
        
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(15, 10, 15, 10)
        container_layout.setSpacing(10)

        self._create_header(container_layout)
        
        self._create_text_section()
        self._create_keywords_section()
        self._create_info_section()

        inner_splitter = QSplitter(Qt.Orientation.Vertical)
        inner_splitter.setChildrenCollapsible(False)
        inner_splitter.addWidget(self.keywords_section_widget)
        inner_splitter.addWidget(self.info_section_widget)
        inner_splitter.setSizes([100, 200])

        inner_splitter.setStretchFactor(1, 1)

        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setChildrenCollapsible(False)
        
        self.splitter.addWidget(self.text_section_widget)
        self.splitter.addWidget(inner_splitter)
        self.splitter.setSizes([100, 300])

        self.splitter.setStretchFactor(1, 3)
        
        container_layout.addWidget(self.splitter)
        
        self.main_layout.addWidget(self.main_container)
        self.size_grip = QSizeGrip(self)
        self.apply_modern_stylesheet()
        self.enable_start_button()
    
    def _run_collapse_animation(self):
        header_height = self.title_label.parent().sizeHint().height()
        keywords_needed_height = self.keywords_section_widget.sizeHint().height()
        spacing = self.main_container.layout().spacing()
        margins = self.main_container.layout().contentsMargins()
        
        target_height = header_height + spacing + keywords_needed_height + margins.top() + margins.bottom()
        target_height = max(target_height, self.min_height)
        
        current_geometry = self.geometry()
        target_geometry = QRect(current_geometry.x(), current_geometry.y(), current_geometry.width(), target_height)
        
        self.resize_animation.setStartValue(current_geometry)
        self.resize_animation.setEndValue(target_geometry)
        self.resize_animation.start()

    def _run_expand_animation(self):
        target_height = self.expanded_height
        
        current_geometry = self.geometry()
        target_geometry = QRect(current_geometry.x(), current_geometry.y(), current_geometry.width(), target_height)
        
        self.resize_animation.setStartValue(current_geometry)
        self.resize_animation.setEndValue(target_geometry)
        self.resize_animation.start()

    def _create_header(self, parent_layout):
        header_layout = QHBoxLayout(); header_layout.setSpacing(10)
        self.title_label = QLabel("🎤 LiveNote AI"); self.title_label.setObjectName("title"); self.title_label.setCursor(Qt.CursorShape.SizeAllCursor)
        self.expand_btn = QPushButton(icon=qta.icon('fa5s.compress-arrows-alt', color='#FFFFFF')); self.expand_btn.setFixedSize(30, 30); self.expand_btn.clicked.connect(self.toggle_expansion); self.expand_btn.setObjectName("expandBtn")
        self.start_button = QPushButton(icon=qta.icon('fa5s.play', color='#00FF88'))
        self.stop_button = QPushButton(icon=qta.icon('fa5s.stop', color='#FF6B6B'))
        self.quit_button = QPushButton(icon=qta.icon('fa5s.times', color='#FF6B6B'))
        for btn in [self.start_button, self.stop_button, self.quit_button]: btn.setFixedSize(32, 32); btn.setObjectName("controlBtn")
        self.start_button.clicked.connect(self.on_start_click); self.stop_button.clicked.connect(self.on_stop_click); self.quit_button.clicked.connect(QApplication.instance().quit)
        header_layout.addWidget(self.title_label); header_layout.addStretch()
        header_layout.addWidget(self.expand_btn); header_layout.addWidget(self.start_button); header_layout.addWidget(self.stop_button); header_layout.addWidget(self.quit_button)
        parent_layout.addLayout(header_layout)

    def _create_section_widget(self, object_name, title):
        section_widget = QFrame(); section_widget.setObjectName(object_name)
        section_layout = QVBoxLayout(section_widget); section_layout.setContentsMargins(0, 0, 0, 0); section_layout.setSpacing(0)
        title_label = QLabel(title, objectName="sectionTitle"); section_layout.addWidget(title_label)
        return section_widget, section_layout
    
    def _create_text_section(self):
        self.text_section_widget, layout = self._create_section_widget("textSection", "📝 Live Transcription")
        self.text_display = QTextEdit("Press ▶ to start listening..."); self.text_display.setObjectName("textDisplay"); self.text_display.setReadOnly(True)
        layout.addWidget(self.text_display)

    def _create_keywords_section(self):
        self.keywords_section_widget, layout = self._create_section_widget("keywordsSection", "🔖 Keywords")
        scroll_area = QScrollArea(); scroll_area.setWidgetResizable(True); scroll_area.setObjectName("keywordsScroll")
        container = QWidget()
        self.keywords_layout = FlowLayout(container, margin=5, spacing=5)
        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)

    def _create_info_section(self):
        self.info_section_widget, layout = self._create_section_widget("infoSection", "🤖 AI Information")
        self.info_webview = QWebEngineView()
        self.info_webview.setObjectName("infoWebView")
        self.info_webview.page().setBackgroundColor(Qt.GlobalColor.transparent)

        layout.addWidget(self.info_webview, 1)
        
    def position_window(self):
        saved_geo = self.config.get_window_geometry()
        if self.config.ui.remember_position and saved_geo:
            self.setGeometry(*saved_geo)
        else:
            screen_geo = QApplication.primaryScreen().geometry()
            margin, start_width, start_height = 20, self.config.ui.default_width, self.config.ui.default_height
            self.setGeometry(screen_geo.width() - start_width - margin, margin, start_width, start_height)

    def add_keywords(self, keywords_list):
        while self.keywords_layout.count():
            child = self.keywords_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not keywords_list:
            no_keyword_label = QLabel("No keywords extracted yet...")
            no_keyword_label.setStyleSheet("color: #aaa; margin: 10px;")
            self.keywords_layout.addWidget(no_keyword_label)
        else:
            for keyword in keywords_list:
                button = KeywordButton(keyword)
                button.keyword_clicked.connect(self.on_keyword_clicked)
                self.keywords_layout.addWidget(button)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'size_grip'):
            self.size_grip.move(self.width() - self.size_grip.width(), self.height() - self.size_grip.height())

    def toggle_expansion(self):
        is_expanded = self.height() > (self.min_height + self.expanded_height) / 2

        if is_expanded:
            self.expand_btn.setIcon(qta.icon('fa5s.expand-arrows-alt', color='#FFFFFF'))
            
            self.text_section_widget.setVisible(False)
            self.info_section_widget.setVisible(False)
            self.keywords_section_widget.setVisible(True)
            
            QTimer.singleShot(0, self._run_collapse_animation)

        else:
            self.expand_btn.setIcon(qta.icon('fa5s.compress-arrows-alt', color='#FFFFFF'))
            
            self.text_section_widget.setVisible(True)
            self.info_section_widget.setVisible(True)
            
            QTimer.singleShot(0, self._run_expand_animation)

    def update_transcribed_text(self, text):
        self.display_lines.append(text)
        if len(self.display_lines) > 2:
            self.display_lines.pop(0)
        self.text_display.setPlainText("\n\n".join(self.display_lines))
        self.text_display.verticalScrollBar().setValue(self.text_display.verticalScrollBar().maximum())

    def on_keyword_clicked(self, keyword):
        is_expanded = self.height() > (self.min_height + self.expanded_height) / 2
        if not is_expanded:
            self.toggle_expansion()

        self.update_ai_info("<p>Loading...</p>")
        if self.keyword_callback:
            self.keyword_callback(keyword)

    def update_ai_info(self, html_content):
        self.info_webview.setHtml(WebViewStyles.wrap_content(html_content))

    def clear_all(self):
        self.display_lines, self.keywords = [], []
        self.text_display.setPlainText("Press ▶ to start listening...")
        self.add_keywords([])
        self.update_ai_info("")

    def apply_modern_stylesheet(self):
        self.setStyleSheet(UIStyles.get_combined_stylesheet())
        
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
        
    def moveEvent(self, event):
        super().moveEvent(event)

    def closeEvent(self, event):
        if self.config and self.config.ui.remember_position:
            geo = self.geometry()
            self.config.save_window_geometry(geo.x(), geo.y(), geo.width(), geo.height())
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.title_label.underMouse():
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, '_drag_pos') and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = None

    def set_keywords(self, keywords_list):
        self.keywords = keywords_list
        self.add_keywords(keywords_list)