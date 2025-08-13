import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import json
import threading
from datetime import datetime
import ollama
from PIL import Image, ImageTk

DEF_MODEL = "llama3.2-rover:3b"
CONFIG_FILE = "config.json"
GEOMETRY = "100x100"
# Geometry to tuple function
to_tuple = lambda s: tuple(map(int, s.split('x')))

class DesktopCompanion:
    def __init__(self, model:str):
        self.root = tk.Tk()
        self.chat_window = None
        self.chat_visible = False
        self.messages = []
        
        # Initialize in correct order
        self.setup_window()
        self.setup_character()
        self.load_config()
        
    def setup_window(self):
        # Window properties
        self.root.title("Desktop Companion")
        self.root.geometry(GEOMETRY)
        
        # Always on top and no taskbar
        self.root.wm_attributes("-topmost", True)
        self.root.overrideredirect(True)  # Remove window decorations
        
        # Transparent background (works on some systems)
        self.root.configure(bg='white')
        try:
            self.root.wm_attributes("-transparentcolor", "black")
        except:
            pass  # Ignore if not supported
        # Position at bottom-right corner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - 120
        y = screen_height - 120
        self.root.geometry(f"{GEOMETRY}+{x}+{y}")
        
        # Make draggable
        self.root.bind("<Button-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.drag)
        
    def setup_character(self):
        # Character frame
        self.char_frame = tk.Frame(self.root, bg='black', width=100, height=100)
        self.char_frame.pack(pady=5)

        image = Image.open("assets/rover.png")
        image = image.resize(to_tuple(GEOMETRY))
        self.char_image = ImageTk.PhotoImage(image)

        self.char_label = tk.Label(self.char_frame, image=self.char_image)
        self.char_label.pack()

        # Click to toggle chat bubble
        self.char_label.bind("<Button-1>", self.toggle_chat_bubble)

    def change_character(self):
        if self.chat_visible:
            image = Image.open("assets/rover-searching.png")
        else:
            image = Image.open("assets/rover.png")

        image = image.resize(to_tuple(GEOMETRY))
        self.char_image = ImageTk.PhotoImage(image)

        self.char_label.configure(image=self.char_image)
        self.char_label.image = self.char_image

    def create_chat_window(self):
        if self.chat_window:
            return
            
        # Create chat bubble window - NORMAL window that can receive focus
        self.chat_window = tk.Toplevel(self.root)
        self.chat_window.title("💬 Chat")
        self.chat_window.wm_attributes("-topmost", True)
        # Remove overrideredirect to allow proper focus
        self.chat_window.configure(bg='#f0f0f0')
        self.chat_window.resizable(False, False)
        
        # Position above character
        char_x = self.root.winfo_x()
        char_y = self.root.winfo_y()
        bubble_x = char_x - 150
        bubble_y = char_y - 300
        self.chat_window.geometry(f"300x250+{bubble_x}+{bubble_y}")
        
        # Handle window close button
        self.chat_window.protocol("WM_DELETE_WINDOW", self.hide_chat_bubble)
        
        # Chat bubble content frame
        bubble_frame = tk.Frame(self.chat_window, bg='white', relief='raised', bd=1)
        bubble_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Chat history area
        self.chat_history = scrolledtext.ScrolledText(
            bubble_frame, 
            height=10, 
            width=35,
            font=("Arial", 9),
            bg='#f8f9fa',
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.chat_history.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Input frame
        input_frame = tk.Frame(bubble_frame, bg='white')
        input_frame.pack(fill='x', padx=5, pady=5)
        
        # Make input field larger and more visible
        self.entry = tk.Entry(input_frame, font=("Arial", 10), relief='solid', bd=1)
        self.entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.entry.bind("<Return>", self.send_message)
        
        send_btn = tk.Button(input_frame, text="Send", command=self.send_message,
                           bg='#4a90e2', fg='white', font=("Arial", 9, "bold"),
                           relief='flat', cursor="hand2")
        send_btn.pack(side='right')
        
        # Force focus on the entry field
        self.chat_window.after(100, lambda: self.entry.focus_force())
        
        # Add welcome message
        welcome_msg = "Hi! I'm Rover."
        self.add_message("Companion", welcome_msg)
        self.messages.append({"role": "assistant", "content": welcome_msg})
        
    def toggle_chat_bubble(self, event=None):
        if self.chat_visible:
            self.hide_chat_bubble()
        else:
            self.show_chat_bubble()
            
    def show_chat_bubble(self):
        if not self.chat_window:
            self.create_chat_window()
        else:
            self.chat_window.deiconify()
            # Bring window to front and focus
            self.chat_window.lift()
            self.chat_window.after(50, lambda: self.entry.focus_force())
        self.chat_visible = True
        self.change_character()
        
    def hide_chat_bubble(self):
        if self.chat_window:
            self.chat_window.withdraw()
        self.chat_visible = False
        self.change_character()
        
    def add_message(self, sender, message):
        if not self.chat_window or not hasattr(self, 'chat_history'):
            return
            
        timestamp = datetime.now().strftime("%H:%M")
        
        self.chat_history.config(state=tk.NORMAL)
        
        # Different styling for user vs companion
        if sender == "You":
            self.chat_history.insert(tk.END, f"[{timestamp}] You: ", "user_tag")
            self.chat_history.insert(tk.END, f"{message}\n\n")
        else:
            self.chat_history.insert(tk.END, f"[{timestamp}] Rover: ", "companion_tag")
            self.chat_history.insert(tk.END, f"{message}\n\n")
        
        # Configure tags for styling
        self.chat_history.tag_config("user_tag", foreground="#2c5aa0", font=("Arial", 9, "bold"))
        self.chat_history.tag_config("companion_tag", foreground="#e91e63", font=("Arial", 9, "bold"))
        
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)  # Scroll to bottom
        
    def send_message(self, event=None):
        message = self.entry.get().strip()
        # Clear input
        self.entry.delete(0, tk.END)
        
        if message == "/clear":
                self.clear_chat_history()
                return
        elif message == "/bye":
                self.clear_chat_history()
                self.toggle_chat_bubble()
                return
        elif message:
            # Add user message to message history
            self.add_message("You", message)
            self.messages.append({"role": "user", "content": message})
            
            # Make the call to Ollama in a separate thread so that the GUI doesn't freeze
            def get_response():
                try:
                    response = ollama.chat(model=self.model, messages=self.messages)
                    reply = response['message']['content']
                    
                    # Add AI respond to the message history
                    self.messages.append({"role": "assistant", "content": reply})
                    
                    self.root.after(0, lambda: self.add_message("Companion", reply))
                except Exception as e:
                    self.root.after(0, lambda: self.add_message("Companion", f"⚠️ Error: {e}"))
            
            threading.Thread(target=get_response, daemon=True).start()
            
    def clear_chat_history(self):
        # If the chat window exists and the chat_history widget is defined
        if self.chat_window and hasattr(self, 'chat_history'):
            # Allow editing
            self.chat_history.config(state=tk.NORMAL)
            # Delete all content
            self.chat_history.delete("1.0", tk.END)
            # Make it read-only again
            self.chat_history.config(state=tk.DISABLED)
            
            # Clear message history list too
            self.messages.clear()

            # Add welcome message
            welcome_msg = "Hi! I'm Rover."
            self.add_message("Companion", welcome_msg)
            self.messages.append({"role": "assistant", "content": welcome_msg})

    def open_settings(self):
        # Create a settings window
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Settings")
        settings_win.geometry("300x600")
        settings_win.resizable(False, False)

        # Model setting
        tk.Label(settings_win, text="Ollama Model:").pack(anchor="w", padx=10, pady=(10, 0))
        # List of available models
        available_models = [
            DEF_MODEL
        ]
        model_var = tk.StringVar(value=getattr(self, "model", DEF_MODEL))
        # Create OptionMenu
        model_menu = tk.OptionMenu(settings_win, model_var, *available_models)
        
        # Menu width
        model_menu.config(width=25)
        # Pack the menu
        model_menu.pack(fill="x", padx=10, pady=5)

        # Save button
        def save_settings():
            self.model = model_var.get()
            self.save_config()
            settings_win.destroy()

        tk.Button(
            settings_win,
            text="Save Settings",
            command=save_settings,
            bg="#4a90e2",
            fg="white"
        ).pack(pady=15)

        # Center the settings window
        def center_window(win):
            win.update_idletasks()
            w = win.winfo_width()
            h = win.winfo_height()
            sw = win.winfo_screenwidth()
            sh = win.winfo_screenheight()
            x = (sw - w) // 2
            y = (sh - h) // 2
            win.geometry(f"{w}x{h}+{x}+{y}")
        center_window(settings_win)

    def save_config(self):
        config = {
            "model": getattr(self, "model", DEF_MODEL)
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)

    def load_config(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                self.model = config.get("model", DEF_MODEL)
        except FileNotFoundError:
            self.model = DEF_MODEL
            
    def start_drag(self, event):
        self.start_x = event.x
        self.start_y = event.y
        
    def drag(self, event):
        x = self.root.winfo_x() + event.x - self.start_x
        y = self.root.winfo_y() + event.y - self.start_y
        self.root.geometry(f"+{x}+{y}")
        
    def run(self):
        # Right-click menu to close
        def show_menu(event):
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Clear Chat", command=self.clear_chat_history)
            menu.add_command(label="Settings", command=self.open_settings)
            menu.add_separator()
            menu.add_command(label="Close", command=self.close_app)
            menu.tk_popup(event.x_root, event.y_root)
            
        def close_app():
            try:
                if self.chat_window:
                    self.chat_window.destroy()
                self.root.quit()
                self.root.destroy()
            except:
                pass
            
        self.close_app = close_app
        self.root.bind("<Button-3>", show_menu)
        
        self.root.mainloop()

if __name__ == "__main__":    
    try:
        model = DEF_MODEL
        ollama.chat(model=model)
        companion = DesktopCompanion(model=model)
        companion.run()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")
