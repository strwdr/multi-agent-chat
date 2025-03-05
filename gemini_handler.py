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

import google.generativeai as genai
from api_handler import APIHandler

class GeminiHandler(APIHandler):
    """Handler for Google Gemini API interactions."""
    
    def __init__(self, logger, api_key=None):
        """Initialize the Gemini handler.
        
        Args:
            logger: The logger instance
            api_key: The Gemini API key
        """
        super().__init__(logger)
        self.api_key = api_key
        self.client = None
        if api_key:
            self.set_api_key(api_key)
    
    def set_api_key(self, api_key):
        """Set the Gemini API key.
        
        Args:
            api_key: The Gemini API key
        """
        self.api_key = api_key
        try:
            genai.configure(api_key=api_key)
            self.client = genai
            if self.logger:
                self.logger.log("Gemini API key set", "Gemini")
        except Exception as e:
            self._show_error(f"Invalid Gemini API key: {str(e)}")
    
    def get_available_models(self):
        """Get a list of available Gemini models.
        
        Returns:
            List of model names or empty list if error
        """
        if not self.api_key or not self.client:
            self._show_error("API key not set. Please set your Gemini API key.")
            return []
            
        try:
            models = [model.name for model in self.client.list_models() 
                     if "gemini" in model.name]
            if self.logger:
                self.logger.log(f"Loaded {len(models)} Gemini models", "Gemini")
            return models
        except Exception as e:
            self._show_error(f"Error fetching Gemini models: {str(e)}")
            # Return known models as fallback
            models = ["gemini-1.0-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
            if self.logger:
                self.logger.log(f"Using fallback list of {len(models)} Gemini models", "Gemini")
            return models
    
    def get_response(self, prompt):
        """Get a response from Gemini for the given prompt.
        
        Args:
            prompt: The user's message to send to Gemini
            
        Returns:
            The AI's response text
        """
        if not self.api_key or not self.client:
            if self.logger:
                self.logger.log("API key not set", "Error")
            return "Error: Gemini API key not set"
            
        if not self.selected_model:
            if self.logger:
                self.logger.log("No model selected", "Error")
            return "Error: No model selected"
        
        # Convert conversation history to Gemini format
        history = []
        
        # Add conversation history
        for msg in self.conversation_history:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                history.append({"role": "user", "parts": [content]})
            elif role == "assistant":
                history.append({"role": "model", "parts": [content]})
        
        try:
            if self.logger:
                self.logger.log(f"Sending prompt to {self.selected_model}", "Gemini")
            
            # Initialize the model
            model = self.client.GenerativeModel(self.selected_model)
            
            # Create a chat session
            chat = model.start_chat(history=history)
            
            # Add system prompt if available
            generation_config = {}
            if self.system_prompt:
                generation_config["system_instruction"] = self.system_prompt
            
            # Send the prompt and get response
            response = chat.send_message(
                prompt,
                generation_config=generation_config if self.system_prompt else None
            )
            
            assistant_response = response.text
            
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            
            return assistant_response
        except Exception as e:
            if self.logger:
                self.logger.log(f"Error generating response: {str(e)}", "Error")
            self._show_error(f"Gemini API error: {str(e)}")
            return f"Error: Could not generate response - {str(e)}"
