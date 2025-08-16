import tkinter as tk
from tkinter import scrolledtext, messagebox

class MainWindow:
    def __init__(self, root, start_callback, stop_callback):
        self.root = root
        self.root.title("LiveNote - Real-time Transcription")
        self.root.geometry("800x600")
        
        # Callbacks
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        
        print("Creating MainWindow UI components...")
        
        self.create_widgets()
        
    def create_widgets(self):
        """Tạo tất cả UI components"""
        
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title label
        title_label = tk.Label(
            main_frame, 
            text="LiveNote - Real-time Audio Transcription", 
            font=("Arial", 16, "bold"),
            fg="blue"
        )
        title_label.pack(pady=(0, 10))
        
        # Text area với scrollbar
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.text_area = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=("Arial", 12),
            bg="white",
            fg="black",
            insertbackground="blue"
        )
        self.text_area.pack(fill='both', expand=True)
        
        # Thêm placeholder text
        self.text_area.insert("1.0", "Sẵn sàng ghi âm...\nNhấn 'Bắt đầu ghi' để bắt đầu transcription.\n\n")
        
        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Start button
        self.start_button = tk.Button(
            button_frame,
            text="Bắt đầu ghi",
            command=self.on_start_click,
            font=("Arial", 12, "bold"),
            bg="green",
            fg="white",
            padx=20,
            pady=10
        )
        self.start_button.pack(side='left', padx=(0, 10))
        
        # Stop button
        self.stop_button = tk.Button(
            button_frame,
            text="Dừng ghi",
            command=self.on_stop_click,
            font=("Arial", 12, "bold"),
            bg="red",
            fg="white",
            padx=20,
            pady=10,
            state='disabled'
        )
        self.stop_button.pack(side='left', padx=(0, 10))
        
        # Clear button
        self.clear_button = tk.Button(
            button_frame,
            text="Xóa text",
            command=self.clear_text,
            font=("Arial", 10),
            bg="orange",
            fg="white",
            padx=15,
            pady=10
        )
        self.clear_button.pack(side='left', padx=(0, 10))
        
        # Status label
        self.status_label = tk.Label(
            button_frame,
            text="Trạng thái: Sẵn sàng",
            font=("Arial", 10),
            fg="green"
        )
        self.status_label.pack(side='right')
        
        print("MainWindow UI components created successfully!")
    
    def on_start_click(self):
        """Handle start button click"""
        print("Start button clicked!")
        self.update_status("Đang bắt đầu...")
        
        try:
            if self.start_callback:
                self.start_callback()
            else:
                print("No start_callback defined!")
                self.update_transcribed_text("Lỗi: Không có start_callback!\n")
        except Exception as e:
            print(f"Error in start callback: {e}")
            self.update_transcribed_text(f"Lỗi khi bắt đầu: {e}\n")
            self.update_status("Lỗi khi bắt đầu")
    
    def on_stop_click(self):
        """Handle stop button click"""
        print("Stop button clicked!")
        self.update_status("Đang dừng...")
        
        try:
            if self.stop_callback:
                self.stop_callback()
            else:
                print("No stop_callback defined!")
                self.update_transcribed_text("Lỗi: Không có stop_callback!\n")
        except Exception as e:
            print(f"Error in stop callback: {e}")
            self.update_transcribed_text(f"Lỗi khi dừng: {e}\n")
            self.update_status("Lỗi khi dừng")
    
    def clear_text(self):
        """Clear text area"""
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert("1.0", "Text đã được xóa.\n\n")
        print("Text area cleared")
    
    def update_transcribed_text(self, text):
        """Thêm text vào text area"""
        try:
            self.text_area.insert(tk.END, text)
            self.text_area.see(tk.END)  # Scroll to bottom
        except Exception as e:
            print(f"Error updating text: {e}")
    
    def update_status(self, status_text):
        """Update status label"""
        try:
            self.status_label.config(text=f"Trạng thái: {status_text}")
        except Exception as e:
            print(f"Error updating status: {e}")
    
    def enable_stop_button(self):
        """Enable stop button, disable start button"""
        try:
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.update_status("🎤 Đang ghi âm...")
            print("UI: Stop button enabled, start button disabled")
        except Exception as e:
            print(f"Error enabling stop button: {e}")
    
    def enable_start_button(self):
        """Enable start button, disable stop button"""
        try:
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.update_status("Sẵn sàng")
            print("UI: Start button enabled, stop button disabled")
        except Exception as e:
            print(f"Error enabling start button: {e}")

# Test nếu chạy file này trực tiếp
if __name__ == "__main__":
    def dummy_start():
        print("Dummy start function called")
        
    def dummy_stop():
        print("Dummy stop function called")
    
    root = tk.Tk()
    window = MainWindow(root, dummy_start, dummy_stop)
    
    print("Testing MainWindow standalone...")
    root.mainloop()