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

import anthropic
from api_handler import APIHandler

class AnthropicHandler(APIHandler):
    """Handler for Anthropic API interactions."""
    
    def __init__(self, logger, api_key=None):
        """Initialize the Anthropic handler.
        
        Args:
            logger: The logger instance
            api_key: The Anthropic API key
        """
        super().__init__(logger)
        self.api_key = api_key
        self.client = None
        if api_key:
            self.set_api_key(api_key)
    
    def set_api_key(self, api_key):
        """Set the Anthropic API key.
        
        Args:
            api_key: The Anthropic API key
        """
        self.api_key = api_key
        try:
            self.client = anthropic.Anthropic(api_key=api_key)
            if self.logger:
                self.logger.log("Anthropic API key set", "Anthropic")
        except Exception as e:
            self._show_error(f"Invalid Anthropic API key: {str(e)}")
    
    def get_available_models(self):
        """Get a list of available Anthropic models.
        
        Returns:
            List of model names or empty list if error
        """
        if not self.api_key or not self.client:
            self._show_error("API key not set. Please set your Anthropic API key.")
            return []
            
        # Anthropic doesn't have a list models endpoint, so we return the known models
        models = ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
        if self.logger:
            self.logger.log(f"Loaded {len(models)} Anthropic models", "Anthropic")
        return models
    
    def get_response(self, prompt):
        """Get a response from Anthropic for the given prompt.
        
        Args:
            prompt: The user's message to send to Anthropic
            
        Returns:
            The AI's response text
        """
        if not self.api_key or not self.client:
            if self.logger:
                self.logger.log("API key not set", "Error")
            return "Error: Anthropic API key not set"
            
        if not self.selected_model:
            if self.logger:
                self.logger.log("No model selected", "Error")
            return "Error: No model selected"
        
        # Convert conversation history to Anthropic format
        messages = []
        
        # Add system prompt if available
        system_prompt = self.system_prompt if self.system_prompt else ""
        
        # Add conversation history
        for msg in self.conversation_history:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                messages.append({"role": "user", "content": content})
            elif role == "assistant":
                messages.append({"role": "assistant", "content": content})
        
        # Add current prompt
        self.conversation_history.append({"role": "user", "content": prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            if self.logger:
                self.logger.log(f"Sending prompt to {self.selected_model}", "Anthropic")
            
            response = self.client.messages.create(
                model=self.selected_model,
                messages=messages,
                system=system_prompt,
                max_tokens=1024
            )
            
            assistant_response = response.content[0].text
            self.conversation_history.append(
                {"role": "assistant", "content": assistant_response}
            )
            return assistant_response
        except Exception as e:
            if self.logger:
                self.logger.log(f"Error generating response: {str(e)}", "Error")
            self._show_error(f"Anthropic API error: {str(e)}")
            return f"Error: Could not generate response - {str(e)}"
