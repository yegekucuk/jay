import json
import sys
from tkinter import messagebox
from OllamaHandler import OllamaHandler
from WindowHandler import WindowHandler

CONFIG_FILE = "config.json"

class DesktopCompanion():
    def __init__(self):
        self.ollama_handler = OllamaHandler()
        self.window_handler = WindowHandler()
        
        # Load config first
        self.load_config()
        
        # Initialize handlers
        self.ollama_handler.initialize()
        self.window_handler.initialize()
        
        # Connect callbacks
        self.setup_callbacks()
        
    def setup_callbacks(self):
        """Setup callbacks between handlers"""
        # Window -> Ollama
        self.window_handler.set_message_callback(self.handle_message)
        self.window_handler.set_clear_callback(self.handle_clear_chat)
        self.window_handler.set_close_callback(self.handle_close_app)
        self.window_handler.set_settings_callback(self.handle_settings_save)
        
        # Ollama -> Window (async response)
        self.ollama_handler.set_response_callback(self.handle_response)
        
        # Override settings handler in window
        self.window_handler.handle_settings = self.handle_settings_open
        
        # Update model label
        self.window_handler.update_model_label(self.ollama_handler.model)
    
    def handle_message(self, message: str):
        """Handle message from window"""
        self.ollama_handler.send_message(message)
    
    def handle_response(self, response: str):
        """Handle response from ollama (called from thread)"""
        self.window_handler.root.after(0, lambda: self.window_handler.add_message("Companion", response))
    
    def handle_clear_chat(self):
        """Handle clear chat request"""
        self.ollama_handler.clear_history()
        self.window_handler.clear_chat_display()
        self.window_handler.add_welcome_message()
    
    def handle_settings_open(self):
        """Handle settings window opening"""
        try:
            available_models = self.ollama_handler.get_available_models()
            self.window_handler.open_settings(
                self.ollama_handler.model,
                self.ollama_handler.name or "",
                available_models
            )
        except Exception as e:
            messagebox.showerror("Error", f"Could not load models: {e}")
    
    def handle_settings_save(self, model: str, name: str):
        """Handle settings save"""
        self.ollama_handler.set_model(model)
        self.ollama_handler.set_name(name)
        self.save_config()
        self.handle_clear_chat()
        self.window_handler.update_model_label(model)
    
    def handle_close_app(self):
        """Handle app close"""
        self.ollama_handler.cleanup()
        self.window_handler.cleanup()
    
    def load_config(self):
        """Load configuration"""
        try:
            available_models = self.ollama_handler.get_available_models()
            if not available_models:
                messagebox.showerror(
                    "No Models Found",
                    "No Ollama models are installed. Please install at least one model using:\n\n"
                    "ollama pull <model_name>\n\n"
                    "For example: ollama pull llama3.2:3b"
                )
                sys.exit(1)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to Ollama: {e}")
            sys.exit(1)
        
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                saved_model = config.get("model", "")
                
                if saved_model in available_models:
                    model = saved_model
                else:
                    model = available_models[0]
                
                name = config.get("name", None)
        except FileNotFoundError:
            model = available_models[0]
            name = None
        
        self.ollama_handler.model = model
        self.ollama_handler.name = name
    
    def save_config(self):
        """Save configuration"""
        config = {
            "model": self.ollama_handler.model,
            "name": self.ollama_handler.name
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    
    def run(self):
        """Run the application"""
        self.window_handler.run()

if __name__ == "__main__":
    try:
        app = DesktopCompanion()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)
