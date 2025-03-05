# Copyright (C) 2025 Jakub Budrewicz
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from abc import ABC, abstractmethod
from tkinter import messagebox
import requests

class APIHandler(ABC):
    """Abstract base class for API handlers."""
    
    def __init__(self, logger):
        """Initialize the API handler.
        
        Args:
            logger: The logger instance
        """
        self.logger = logger
        self.conversation_history = []
        self.selected_model = None
        self.system_prompt = None
    
    @abstractmethod
    def get_available_models(self):
        """Get a list of available models.
        
        Returns:
            List of model names or empty list if error
        """
        pass
    
    def set_model(self, model_name):
        """Set the active model.
        
        Args:
            model_name: The name of the model to use
        """
        self.selected_model = model_name
        if self.logger:
            self.logger.log(f"Selected model: {model_name}", self.__class__.__name__)
            
    def set_system_prompt(self, system_prompt):
        """Set the system prompt for the conversation.
        
        Args:
            system_prompt: The system prompt to use
        """
        self.system_prompt = system_prompt
        if self.logger:
            self.logger.log(f"Set system prompt for {self.selected_model}", self.__class__.__name__)
    
    @abstractmethod
    def get_response(self, prompt):
        """Get a response from the API for the given prompt.
        
        Args:
            prompt: The user's message to send to the API
            
        Returns:
            The AI's response text
        """
        pass
    
    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
        if self.logger:
            self.logger.log("Conversation history cleared", self.__class__.__name__)
    
    def get_conversation_history(self):
        """Get the current conversation history.
        
        Returns:
            List of conversation messages including system prompt
        """
        # Create a full history including the system prompt
        full_history = []
        if self.system_prompt:
            full_history.append({"role": "system", "content": self.system_prompt})
        full_history.extend(self.conversation_history)
        return full_history
    
    def get_conversation_length(self):
        """Get the number of messages in the conversation history.
        
        Returns:
            Number of messages
        """
        return len(self.conversation_history)
    
    def _show_error(self, message):
        """Show error message when API is not available.
        
        Args:
            message: The error message to display
        """
        if self.logger:
            self.logger.log(f"Error: {message}", "Error")
        # Only show error message box if it's not during initialization
        if self.logger and hasattr(self.logger, 'initialized') and self.logger.initialized:
            messagebox.showerror(f"{self.__class__.__name__} Error", message)
