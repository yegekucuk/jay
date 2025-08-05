import tkinter as tk
from tkinter import scrolledtext
import threading
from datetime import datetime
import ollama
from PIL import Image, ImageTk

GEOMETRY = "100x100"
# Geometry to tuple function
to_tuple = lambda s: tuple(map(int, s.split('x')))

class DesktopCompanion:
    def __init__(self):
        self.root = tk.Tk()
        self.chat_window = None
        self.chat_visible = False
        self.messages = []
        
        # Initialize in correct order
        self.setup_window()
        self.setup_character()
        
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
        self.char_frame = tk.Frame(self.root, bg='black', width=80, height=80)
        self.char_frame.pack(pady=5)

        image = Image.open("assets/rover.png")
        image = image.resize(to_tuple(GEOMETRY))
        self.char_image = ImageTk.PhotoImage(image)

        self.char_label = tk.Label(self.char_frame, image=self.char_image)
        self.char_label.pack()

        # Click to toggle chat bubble
        self.char_label.bind("<Button-1>", self.toggle_chat_bubble)
        
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
        
    def hide_chat_bubble(self):
        if self.chat_window:
            self.chat_window.withdraw()
        self.chat_visible = False
        
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
        if message:
            # Add user message to history
            self.add_message("You", message)
            
            # 1. Mesaj geçmişine kullanıcı mesajını ekle
            self.messages.append({"role": "user", "content": message})
            
            # 2. Ollama çağrısını ayrı bir thread içinde yap ki GUI donmasın
            def get_response():
                try:
                    response = ollama.chat(model='rover:latest', messages=self.messages)
                    reply = response['message']['content']
                    
                    # 3. Mesaj geçmişine AI cevabını ekle
                    self.messages.append({"role": "assistant", "content": reply})
                    
                    self.root.after(0, lambda: self.add_message("Companion", reply))
                except Exception as e:
                    self.root.after(0, lambda: self.add_message("Companion", f"⚠️ Error: {e}"))
            
            threading.Thread(target=get_response, daemon=True).start()
            
            # Clear input
            self.entry.delete(0, tk.END)

            
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
            menu.add_command(label="Toggle Chat", command=self.toggle_chat_bubble)
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
        ollama.chat(model="rover:latest")
        companion = DesktopCompanion()
        companion.run()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")
