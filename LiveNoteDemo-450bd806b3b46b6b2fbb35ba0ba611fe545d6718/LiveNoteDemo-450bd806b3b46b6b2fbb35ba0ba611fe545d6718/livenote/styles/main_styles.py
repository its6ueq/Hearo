# file: livenote/styles/main_styles.py

class UIStyles:
    
    @staticmethod
    def get_main_window_style():
        return """
            #mainContainer {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(35, 39, 42, 0.95),
                    stop:1 rgba(25, 28, 31, 0.95));
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                backdrop-filter: blur(10px);
            }
            
            #resizeHandle {
                background: rgba(0, 255, 136, 0.3);
                border-radius: 2px;
            }
            #resizeHandle:hover {
                background: rgba(0, 255, 136, 0.6);
            }
        """
    
    @staticmethod
    def get_header_styles():
        return """
            #title {
                color: #FFFFFF;
                font-weight: bold;
                font-size: 14px;
            }
            
            #expandBtn {
                background: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 15px;
                padding: 5px;
                min-width: 30px;
                max-width: 30px;
            }
            #expandBtn:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: scale(1.05);
            }
            #expandBtn:pressed {
                background: rgba(255, 255, 255, 0.3);
            }
            
            #controlBtn {
                background: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 16px;
                padding: 6px;
                min-width: 32px;
                max-width: 32px;
            }
            #controlBtn:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: scale(1.05);
            }
            #controlBtn:pressed {
                background: rgba(255, 255, 255, 0.3);
            }
        """
    
    @staticmethod
    def get_section_styles():
        return """
            #textSection, #keywordsSection, #infoSection {
                background: rgba(0, 0, 0, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                margin: 2px 0px;
            }
            
            #sectionTitle {
                color: #00FF88;
                font-weight: bold;
                font-size: 13px;
                margin: 0px 0px 5px 0px;
                padding: 0px;
            }
        """
    
    @staticmethod
    def get_text_display_styles():
        return """
            #textDisplay {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 6px;
                color: #e0e1e2;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 14px;
                padding: 12px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                selection-background-color: rgba(0, 255, 136, 0.3);
                line-height: 1.4;
            }
            #textDisplay:focus {
                border: 1px solid rgba(0, 255, 136, 0.3);
            }
        """
    
    @staticmethod
    def get_scrollbar_styles():
        return """
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.1);
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                min-height: 20px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(0, 255, 136, 0.5);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            
            QScrollBar:horizontal {
                background: rgba(255, 255, 255, 0.1);
                height: 8px;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                min-width: 20px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgba(0, 255, 136, 0.5);
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
                width: 0px;
            }
        """
    
    @staticmethod
    def get_keyword_styles():
        return """
            #keywordsScroll {
                background: transparent;
                border: none;
                min-height: 50px;
            }
            
            KeywordButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 255, 136, 0.2),
                    stop:1 rgba(0, 200, 108, 0.2));
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 14px;
                color: #FFFFFF;
                font-size: 12px;
                font-weight: 500;
                padding: 6px 14px;
                min-width: 60px;
                margin: 2px;
            }
            KeywordButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 255, 136, 0.4),
                    stop:1 rgba(0, 200, 108, 0.4));
                border: 1px solid rgba(0, 255, 136, 0.6);
                transform: scale(1.05);
            }
            KeywordButton:pressed {
                background: rgba(0, 255, 136, 0.6);
                transform: scale(0.95);
            }
        """
    
    @staticmethod
    def get_info_section_styles():
        return """
            #infoWebView {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 6px;
                min-height: 150px;
            }
        """
    
    @staticmethod
    def get_scroll_area_styles():
        return """
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """
        
    @staticmethod
    def get_splitter_style():
        return """
            QSplitter::handle:vertical {
                height: 5px;
                background-color: rgba(255, 255, 255, 0.05);
            }
            QSplitter::handle:vertical:hover {
                background-color: rgba(0, 255, 136, 0.3);
            }
            QSplitter::handle:vertical:pressed {
                background-color: rgba(0, 255, 136, 0.5);
            }
        """
        
    @staticmethod
    def get_sizegrip_style():
        return """
            QSizeGrip {
                background-color: transparent;
            }
        """
        
    @staticmethod
    def get_combined_stylesheet():
        """Get all styles combined"""
        return (
            UIStyles.get_main_window_style() +
            UIStyles.get_header_styles() +
            UIStyles.get_section_styles() +
            UIStyles.get_text_display_styles() +
            UIStyles.get_scrollbar_styles() +
            UIStyles.get_keyword_styles() +
            UIStyles.get_info_section_styles() +
            UIStyles.get_scroll_area_styles() +
            UIStyles.get_splitter_style() +
            UIStyles.get_sizegrip_style() 

        )

class WebViewStyles:
    @staticmethod
    def get_dark_theme_wrapper():
        return """
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background-color: #2f3136 !important; 
                color: #dcddde !important; 
                margin: 15px;
                line-height: 1.6;
                font-size: 14px;
            }
            h1, h2, h3, h4, h5, h6 {
                color: #ffffff !important;
                border-bottom: 2px solid rgba(0, 255, 136, 0.3);
                padding-bottom: 5px;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            p {
                margin: 10px 0;
                color: #dcddde !important;
            }
            a {
                color: #00d4aa !important;
                text-decoration: none;
            }
            a:hover {
                color: #00FF88 !important;
                text-decoration: underline;
            }
            ul, ol {
                padding-left: 20px;
                margin: 10px 0;
            }
            li {
                margin: 5px 0;
                color: #dcddde !important;
            }
            code {
                background: rgba(0, 0, 0, 0.4) !important;
                color: #00FF88 !important;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
            }
            pre {
                background: rgba(0, 0, 0, 0.4) !important;
                color: #dcddde !important;
                padding: 15px;
                border-radius: 5px;
                border-left: 3px solid #00FF88;
                overflow-x: auto;
                margin: 15px 0;
            }
            blockquote {
                border-left: 3px solid rgba(0, 255, 136, 0.5);
                padding-left: 15px;
                margin: 15px 0;
                color: #b9bbbe !important;
                font-style: italic;
                background: rgba(0, 0, 0, 0.2);
                padding: 10px 15px;
                border-radius: 5px;
            }
            img {
                max-width: 100%;
                height: auto;
                border-radius: 5px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                margin: 10px 0;
            }
            .highlight {
                background: rgba(0, 255, 136, 0.2) !important;
                color: #ffffff !important;
                padding: 2px 4px;
                border-radius: 3px;
            }
            .placeholder {
                text-align: center;
                opacity: 0.7;
                margin-top: 30px;
                padding: 30px;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .loading {
                text-align: center;
                margin-top: 40px;
                padding: 20px;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .spinner {
                display: inline-block;
                width: 24px;
                height: 24px;
                border: 3px solid rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                border-top-color: #00FF88;
                animation: spin 1s ease-in-out infinite;
                margin-bottom: 15px;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            .keyword {
                color: #00FF88 !important;
                font-weight: bold;
            }
            * {
                background-color: #2f3136 !important;
                color: #dcddde !important;
            }
            div, span, strong, em, b, i {
                background: transparent !important;
            }
        </style>
        """
    
    @staticmethod
    def wrap_content(html_content):
        return f"""
        <html>
        <head>
            {WebViewStyles.get_dark_theme_wrapper()}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """