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

from openai import OpenAI
from api_handler import APIHandler

class OpenAIHandler(APIHandler):
    """Handler for OpenAI API interactions."""
    
    def __init__(self, logger, api_key=None):
        """Initialize the OpenAI handler.
        
        Args:
            logger: The logger instance
            api_key: The OpenAI API key
        """
        super().__init__(logger)
        self.api_key = api_key
        self.client = None
        if api_key:
            self.set_api_key(api_key)
    
    def set_api_key(self, api_key):
        """Set the OpenAI API key.
        
        Args:
            api_key: The OpenAI API key
        """
        self.api_key = api_key
        try:
            self.client = OpenAI(api_key=api_key)
            if self.logger:
                self.logger.log("OpenAI API key set", "OpenAI")
        except Exception as e:
            self._show_error(f"Invalid OpenAI API key: {str(e)}")
    
    def get_available_models(self):
        """Get a list of available OpenAI models.
        
        Returns:
            List of model names or empty list if error
        """
        if not self.api_key or not self.client:
            self._show_error("API key not set. Please set your OpenAI API key.")
            return []
            
        try:
            models_list = self.client.models.list()
            # Filter for chat models
            chat_models = [
                model.id for model in models_list.data 
                if model.id.startswith(("gpt-3.5", "gpt-4"))
            ]
            if chat_models and self.logger:
                self.logger.log(f"Loaded {len(chat_models)} OpenAI models", "OpenAI")
            return chat_models
        except Exception as e:
            self._show_error(f"Error fetching OpenAI models: {str(e)}")
            return []
    
    def get_response(self, prompt):
        """Get a response from OpenAI for the given prompt.
        
        Args:
            prompt: The user's message to send to OpenAI
            
        Returns:
            The AI's response text
        """
        if not self.api_key or not self.client:
            if self.logger:
                self.logger.log("API key not set", "Error")
            return "Error: OpenAI API key not set"
            
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
                self.logger.log(f"Sending prompt to {self.selected_model}", "OpenAI")
            
            response = self.client.chat.completions.create(
                model=self.selected_model,
                messages=messages
            )
            
            assistant_response = response.choices[0].message.content
            self.conversation_history.append(
                {"role": "assistant", "content": assistant_response}
            )
            return assistant_response
        except Exception as e:
            if self.logger:
                self.logger.log(f"Error generating response: {str(e)}", "Error")
            self._show_error(f"OpenAI API error: {str(e)}")
            return f"Error: Could not generate response - {str(e)}"
