from Handler import Handler
from abc import abstractmethod
from typing import List, Dict, Any, Optional

class ChatHandler(Handler):
    """Abstract handler for chat functionality"""
    
    @abstractmethod
    def send_message(self, message: str) -> str:
        """Send message and get response"""
        pass
    
    @abstractmethod
    def clear_history(self) -> None:
        """Clear chat history"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        pass
    
    @abstractmethod
    def set_model(self, model: str) -> None:
        """Set the current model"""
        pass
