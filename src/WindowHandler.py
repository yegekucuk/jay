import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime
from PIL import Image, ImageTk
from typing import Callable, Optional
from Handler import Handler

GEOMETRY = "100x100"
fontsize = 11
to_tuple = lambda s: tuple(map(int, s.split('x')))

class WindowHandler(Handler):
    """Handler for GUI window management"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.chat_window = None
        self.chat_visible = False
        self.chat_bubble_width = 750
        self.chat_bubble_height = 500
        
        # Callbacks
        self.on_message_send = None
        self.on_settings_save = None
        self.on_clear_chat = None
        self.on_close_app = None
        
        # UI elements
        self.char_frame = None
        self.char_label = None
        self.char_image = None
        self.chat_history = None
        self.entry = None
        self.model_name_label = None

        # Current model name
        self.current_model = None
        
    def initialize(self) -> None:
        """Initialize the window handler"""
        self.setup_window()
        self.setup_character()
        
    def cleanup(self) -> None:
        """Cleanup window resources"""
        try:
            if self.chat_window:
                self.chat_window.destroy()
            self.root.quit()
            self.root.destroy()
        except:
            pass
    
    def setup_window(self) -> None:
        """Setup main window"""
        self.root.title("Desktop Companion")
        self.root.geometry(GEOMETRY)
        self.root.wm_attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.configure(bg='white')
        
        try:
            self.root.wm_attributes("-transparentcolor", "black")
        except:
            pass
        
        # Position at bottom-right
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - 120
        y = screen_height - 120
        self.root.geometry(f"{GEOMETRY}+{x}+{y}")
        
        # Make draggable
        self.root.bind("<Button-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.drag)
        self.root.bind("<Button-3>", self.show_context_menu)
    
    def setup_character(self) -> None:
        """Setup character display"""
        self.char_frame = tk.Frame(self.root, bg='black', width=100, height=100)
        self.char_frame.pack(pady=5)
        
        image = Image.open("assets/jay.png")
        image = image.resize(to_tuple(GEOMETRY))
        self.char_image = ImageTk.PhotoImage(image)
        
        self.char_label = tk.Label(self.char_frame, image=self.char_image)
        self.char_label.pack()
        self.char_label.bind("<Button-1>", self.toggle_chat_bubble)
    
    def change_character(self) -> None:
        """Change character image based on chat state"""
        if self.chat_visible:
            image = Image.open("assets/jay-active.png")
        else:
            image = Image.open("assets/jay.png")
        
        image = image.resize(to_tuple(GEOMETRY))
        self.char_image = ImageTk.PhotoImage(image)
        self.char_label.configure(image=self.char_image)
        self.char_label.image = self.char_image
    
    def create_chat_window(self) -> None:
        """Create chat window"""
        if self.chat_window:
            return
        
        self.chat_window = tk.Toplevel(self.root)
        self.chat_window.title("💬 Chat")
        self.chat_window.wm_attributes("-topmost", True)
        self.chat_window.configure(bg='#f0f0f0')
        self.chat_window.resizable(True, True)
        
        self.set_chat_bubble_size(self.chat_bubble_width, self.chat_bubble_height)
        self.center_window(self.chat_window)
        
        self.chat_window.protocol("WM_DELETE_WINDOW", self.hide_chat_bubble)
        
        # Model name label
        self.model_name_label = tk.Label(self.chat_window, text="", font=("Arial", fontsize))
        if self.current_model:
            self.model_name_label.config(text=self.current_model)
        self.model_name_label.pack(pady=5)
        
        # Chat frame
        bubble_frame = tk.Frame(self.chat_window, bg='white', relief='raised', bd=1)
        bubble_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Chat history
        self.chat_history = scrolledtext.ScrolledText(
            bubble_frame, height=10, width=35, font=("Arial", fontsize),
            bg='#f8f9fa', wrap=tk.WORD, state=tk.DISABLED
        )
        self.chat_history.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Input frame
        input_frame = tk.Frame(bubble_frame, bg='white')
        input_frame.pack(fill='x', padx=5, pady=5)
        
        self.entry = tk.Entry(input_frame, font=("Arial", fontsize), relief='solid', bd=1)
        self.entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.entry.bind("<Return>", self.handle_message_send)
        
        send_btn = tk.Button(
            input_frame, text="Send", command=self.handle_message_send,
            bg='#4a90e2', fg='white', font=("Arial", fontsize, "bold"),
            relief='flat', cursor="hand2"
        )
        send_btn.pack(side='right')
        
        self.chat_window.after(100, lambda: self.entry.focus_force())
        self.add_welcome_message()
    
    def set_chat_bubble_size(self, width: int, height: int) -> None:
        """Set chat bubble size"""
        self.chat_bubble_width = width
        self.chat_bubble_height = height
        if self.chat_window:
            self.chat_window.geometry(f"{width}x{height}")
    
    def center_window(self, win: tk.Toplevel) -> None:
        """Center window on screen"""
        win.update_idletasks()
        w = win.winfo_width()
        h = win.winfo_height()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")
    
    def add_welcome_message(self) -> None:
        """Add welcome message"""
        self.add_message("Companion", "Welcome back!")
    
    def toggle_chat_bubble(self, event=None) -> None:
        """Toggle chat bubble visibility"""
        if self.chat_visible:
            self.hide_chat_bubble()
        else:
            self.show_chat_bubble()
    
    def show_chat_bubble(self) -> None:
        """Show chat bubble"""
        if not self.chat_window:
            self.create_chat_window()
        else:
            self.chat_window.deiconify()
            self.chat_window.lift()
            self.chat_window.after(50, lambda: self.entry.focus_force())
        self.chat_visible = True
        self.change_character()
    
    def hide_chat_bubble(self) -> None:
        """Hide chat bubble"""
        if self.chat_window:
            self.chat_window.withdraw()
        self.chat_visible = False
        self.change_character()
    
    def add_message(self, sender: str, message: str) -> None:
        """Add message to chat history"""
        if not self.chat_window or not hasattr(self, 'chat_history'):
            return
        
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_history.config(state=tk.NORMAL)
        
        if sender == "You":
            self.chat_history.insert(tk.END, f"[{timestamp}] You: ", "user_tag")
            self.chat_history.insert(tk.END, f"\n{message}\n\n")
        else:
            self.chat_history.insert(tk.END, f"[{timestamp}] Jay: ", "companion_tag")
            self.chat_history.insert(tk.END, f"\n{message}\n\n")
        
        self.chat_history.tag_config("user_tag", foreground="#2c5aa0", font=("Arial", fontsize, "bold"))
        self.chat_history.tag_config("companion_tag", foreground="#e91e63", font=("Arial", fontsize, "bold"))
        
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)
    
    def clear_chat_display(self) -> None:
        """Clear chat display"""
        if self.chat_window and hasattr(self, 'chat_history'):
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.delete("1.0", tk.END)
            self.chat_history.config(state=tk.DISABLED)
    
    def handle_message_send(self, event=None) -> None:
        """Handle message sending"""
        message = self.entry.get().strip()
        self.entry.delete(0, tk.END)
        
        if message == "/clear":
            if self.on_clear_chat:
                self.on_clear_chat()
            return
        elif message == "/bye":
            if self.on_clear_chat:
                self.on_clear_chat()
            self.toggle_chat_bubble()
            return
        elif message and self.on_message_send:
            self.add_message("You", message)
            self.on_message_send(message)
    
    def open_settings(self, current_model: str, current_name: str, available_models: list) -> None:
        """Open settings window"""
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Settings")
        settings_win.geometry("300x600")
        settings_win.resizable(False, False)
        settings_win.wm_attributes("-topmost", True)
        
        # Model setting
        tk.Label(settings_win, text="Ollama Model:").pack(anchor="w", padx=10, pady=(10, 0))
        model_var = tk.StringVar(value=current_model)
        model_menu = tk.OptionMenu(settings_win, model_var, *available_models)
        model_menu.config(width=25)
        model_menu.pack(fill="x", padx=10, pady=5)
        
        # Name setting
        tk.Label(settings_win, text="Your Name:").pack(anchor="w", padx=10, pady=(10, 0))
        name_var = tk.StringVar(value=current_name or "")
        tk.Entry(settings_win, textvariable=name_var, width=30).pack(fill="x", padx=10, pady=5)
        
        def save_settings():
            if self.on_settings_save:
                self.on_settings_save(model_var.get(), name_var.get().strip() or None)
            settings_win.destroy()
        
        # Buttons
        btn_frame = tk.Frame(settings_win)
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="Save Settings", command=save_settings,
                 bg="#4a90e2", fg="white", width=12).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", bg="#4a90e2", fg="white", width=12,
                 command=settings_win.destroy).pack(side="left", padx=5)
        
        self.center_window(settings_win)
    
    def update_model_label(self, model: str) -> None:
        """Update model name label"""
        self.current_model = model
        
        if self.model_name_label:
            self.model_name_label.config(text=self.current_model)
    
    def reset_chat_bubble_size(self) -> None:
        """Reset chat bubble to default size"""
        if self.chat_visible:
            self.set_chat_bubble_size(self.chat_bubble_width, self.chat_bubble_height)
            self.center_window(self.chat_window)
    
    def show_context_menu(self, event) -> None:
        """Show context menu"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Clear Chat", command=lambda: self.on_clear_chat() if self.on_clear_chat else None)
        menu.add_command(label="Settings", command=self.handle_settings)
        menu.add_command(label="Reset Position", command=self.reset_chat_bubble_size)
        menu.add_separator()
        menu.add_command(label="Close", command=lambda: self.on_close_app() if self.on_close_app else None)
        menu.tk_popup(event.x_root, event.y_root)
    
    def handle_settings(self) -> None:
        """Handle settings menu click"""
        # This will be connected by the main app
        pass
    
    def start_drag(self, event) -> None:
        """Start drag operation"""
        self.start_x = event.x
        self.start_y = event.y
    
    def drag(self, event) -> None:
        """Handle drag operation"""
        x = self.root.winfo_x() + event.x - self.start_x
        y = self.root.winfo_y() + event.y - self.start_y
        self.root.geometry(f"+{x}+{y}")
    
    def run(self) -> None:
        """Run the main event loop"""
        self.root.mainloop()
    
    # Callback setters
    def set_message_callback(self, callback: Callable[[str], None]) -> None:
        self.on_message_send = callback
    
    def set_settings_callback(self, callback: Callable[[str, str], None]) -> None:
        self.on_settings_save = callback
    
    def set_clear_callback(self, callback: Callable[[], None]) -> None:
        self.on_clear_chat = callback
    
    def set_close_callback(self, callback: Callable[[], None]) -> None:
        self.on_close_app = callback