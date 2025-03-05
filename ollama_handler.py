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

import ollama
import requests
import os
from api_handler import APIHandler

class OllamaHandler(APIHandler):
    """Handler for Ollama API interactions."""
    
    def __init__(self, logger, address="http://localhost:11434"):
        """Initialize the Ollama handler.
        
        Args:
            logger: The logger instance
            address: The Ollama API address (default: http://localhost:11434)
        """
        super().__init__(logger)
        self.address = address
    
    def get_available_models(self):
        """Get a list of available Ollama models.
        
        Returns:
            List of model names or empty list if error
        """
        try:
            response = requests.get(f'{self.address}/api/tags')
            if response.status_code == 200:
                models = [model['name'] for model in response.json()['models']]
                if models and self.logger:
                    self.logger.log(f"Loaded {len(models)} Ollama models", "Ollama")
                return models
            else:
                self._show_error(f"Cannot connect to Ollama API at {self.address}.\nPlease ensure Ollama is running with:\n\nollama serve")
                return []
        except requests.exceptions.ConnectionError:
            self._show_error(f"Cannot connect to Ollama API at {self.address}.\nPlease ensure Ollama is running with:\n\nollama serve")
            return []
            
    def set_address(self, address):
        """Set the Ollama API address.
        
        Args:
            address: The Ollama API address (e.g., http://localhost:11434)
        """
        self.address = address
        if self.logger:
            self.logger.log(f"Set Ollama API address to: {address}", "Ollama")
    
    def get_response(self, prompt):
        """Get a response from Ollama for the given prompt.
        
        Args:
            prompt: The user's message to send to Ollama
            
        Returns:
            The AI's response text
        """
        if not self.selected_model:
            if self.logger:
                self.logger.log("No model selected", "Error")
            return "Error: No model selected"
        
        # Create messages list with system prompt if available
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add current prompt
        self.conversation_history.append({"role": "user", "content": prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            if self.logger:
                self.logger.log(f"Sending prompt to {self.selected_model}", "Ollama")
            # Configure ollama client with custom address
            os.environ["OLLAMA_HOST"] = self.address
            
            response = ollama.chat(
                model=self.selected_model,
                messages=messages
            )
            assistant_response = response["message"]["content"]
            self.conversation_history.append(
                {"role": "assistant", "content": assistant_response}
            )
            return assistant_response
        except Exception as e:
            if self.logger:
                self.logger.log(f"Error generating response: {str(e)}", "Error")
            self._show_error(f"Cannot connect to Ollama API at {self.address}.\nPlease ensure Ollama is running with:\n\nollama serve")
            return "Error: Could not generate response"
