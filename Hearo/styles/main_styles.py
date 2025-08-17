# file: livenote/styles/main_styles.py

class UIStyles:
    
    @staticmethod
    def get_main_window_style():
        return """
            #mainContainer {
                background-color: #36393F;
                border: 1px solid #202225;
                border-radius: 12px;
            }
            #resizeHandle { ... }
        """
    
    @staticmethod
    def get_header_styles():
        return """
            #title {
                color: #FFFFFF;
                font-size: 16px;
                font-weight: 600;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """
    
    @staticmethod
    def get_section_styles():
        return """
            #textSection, #keywordsSection, #infoSection {
                background-color: transparent;
                border: none;
                padding: 8px;
            }
            
            #sectionTitle {
                color: #B9BBBE;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 4px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """
    
    @staticmethod
    def get_text_display_styles():
        return """
            #textDisplay {
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
            #textDisplay:focus {
                border-color: #5865F2;
                outline: none;
            }
        """
    
    @staticmethod
    def get_scrollbar_styles():
        return """
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
            QSplitter::handle {
                background-color: #40444B;
                border-radius: 2px;
                margin: 2px;
            }
            QSplitter::handle:hover {
                background-color: #5865F2;
            }
            QSplitter::handle:vertical {
                height: 4px;
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
                background-color: #2F3136;
                color: #DCDDDE;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                line-height: 1.6;
                margin: 0;
                padding: 16px;
            }
            
            ::-webkit-scrollbar {
                width: 10px;
                background-color: #2F3136; 
            }

            ::-webkit-scrollbar-thumb {
                background-color: #5865F2; 
                border-radius: 5px;
                border: 2px solid #2F3136;
            }

            ::-webkit-scrollbar-thumb:hover {
                background-color: #4752C4; 
            }

            ::-webkit-scrollbar-corner {
                background: transparent; 
            }
            
            a {
                color: #00AFF4 !important;
                text-decoration: none !important;
            }
            a:hover {
                color: #5865F2 !important;
                text-decoration: underline !important;
            }
            img {
                max-width: 100%;
                height: auto;
                border-radius: 8px;
            }
            p { margin: 0 0 12px 0; }
            h1, h2, h3, h4, h5, h6 {
                color: #FFFFFF;
                margin: 0 0 8px 0;
            }
            code {
                background-color: #202225;
                color: #F47067;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
            pre {
                background-color: #202225;
                padding: 12px;
                border-radius: 6px;
                overflow-x: auto;
            }
            blockquote {
                border-left: 4px solid #5865F2;
                margin: 0;
                padding: 0 0 0 12px;
                color: #B9BBBE;
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