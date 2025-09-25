import ollama
import threading
from typing import List, Dict, Any, Optional, Callable
from Handler import ChatHandler

class OllamaHandler(ChatHandler):
    """Handler for Ollama chat functionality"""
    
    def __init__(self, model: Optional[str] = None, name: Optional[str] = None):
        self.model = model
        self.name = name
        self.messages = []
        self._response_callback = None
        
    def initialize(self) -> None:
        """Initialize the Ollama handler"""
        if self.model:
            # Load model into memory
            ollama.chat(model=self.model, keep_alive=-1)
        self.upsert_system_prompt()
    
    def cleanup(self) -> None:
        """Cleanup Ollama resources"""
        if self.model:
            import os
            os.system(f"ollama stop {self.model}")
    
    def get_available_models(self) -> List[str]:
        """Get list of installed Ollama models"""
        try:
            models_data = ollama.list()
            return sorted([m["model"] for m in models_data["models"]], key=str.lower)
        except Exception as e:
            raise Exception(f"Failed to get Ollama models: {e}")
    
    def set_model(self, model: str) -> None:
        """Set the current model"""
        self.model = model
        # Load model into memory
        ollama.chat(model=self.model, keep_alive=-1)
        self.clear_history()
    
    def set_name(self, name: Optional[str]) -> None:
        """Set user name"""
        self.name = name
        self.upsert_system_prompt()
    
    def set_response_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for async responses"""
        self._response_callback = callback
    
    def send_message(self, message: str) -> None:
        """Send message asynchronously"""
        # Add user message to history
        self.messages.append({"role": "user", "content": message})
        
        def get_response():
            try:
                response = ollama.chat(model=self.model, messages=self.messages, keep_alive=-1)
                reply = response['message']['content']
                
                # Add AI response to history
                self.messages.append({"role": "assistant", "content": reply})
                
                if self._response_callback:
                    self._response_callback(reply)
            except Exception as e:
                error_msg = f"⚠️ Error: {e}"
                if self._response_callback:
                    self._response_callback(error_msg)
        
        threading.Thread(target=get_response, daemon=True).start()
    
    def clear_history(self) -> None:
        """Clear chat history"""
        self.messages.clear()
        self.upsert_system_prompt()
    
    def get_system_prompt(self) -> str:
        """Generate system prompt"""
        prompt = (
            "You are Jay, a helpful personal assistant. \n"
            "Role: provide accurate, concise answers. \n"
            "Constraints: \n"
            "- Keep short replies unless asked to expand.\n"
            "- If the user explicitly asks for more detail or explanation, provide longer, structured responses.\n"
            "- If you are not sure about your answer, DO NOT answer. DO NOT take a guess and DO NOT make assumptions."
        )
        
        if self.name:
            prompt += f"\nThe user's name is {self.name}."
        
        return prompt
    
    def upsert_system_prompt(self) -> None:
        """Update system prompt in message history"""
        sys_text = self.get_system_prompt().strip()
        
        if not sys_text.endswith((".", "!", "?")):
            sys_text += "."
        
        # Remove existing system messages
        self.messages = [m for m in self.messages if m.get("role") != "system"]
        # Insert as first message
        self.messages.insert(0, {"role": "system", "content": sys_text})