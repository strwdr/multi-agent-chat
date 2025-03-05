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

import requests
from api_handler import APIHandler

class GrokHandler(APIHandler):
    """Handler for Grok API interactions."""
    
    def __init__(self, logger, api_key=None):
        """Initialize the Grok handler.
        
        Args:
            logger: The logger instance
            api_key: The Grok API key
        """
        super().__init__(logger)
        self.api_key = api_key
        self.api_base = "https://api.grok.x.com/v1"
        
    def set_api_key(self, api_key):
        """Set the Grok API key.
        
        Args:
            api_key: The Grok API key
        """
        self.api_key = api_key
        if self.logger:
            self.logger.log("Grok API key set", "Grok")
    
    def get_available_models(self):
        """Get a list of available Grok models.
        
        Returns:
            List of model names or empty list if error
        """
        if not self.api_key:
            self._show_error("API key not set. Please set your Grok API key.")
            return []
            
        # Grok doesn't have a public list models endpoint yet, so we return the known models
        models = ["grok-1", "grok-2"]
        if self.logger:
            self.logger.log(f"Loaded {len(models)} Grok models", "Grok")
        return models
    
    def get_response(self, prompt):
        """Get a response from Grok for the given prompt.
        
        Args:
            prompt: The user's message to send to Grok
            
        Returns:
            The AI's response text
        """
        if not self.api_key:
            if self.logger:
                self.logger.log("API key not set", "Error")
            return "Error: Grok API key not set"
            
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
                self.logger.log(f"Sending prompt to {self.selected_model}", "Grok")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.selected_model,
                "messages": messages,
                "max_tokens": 1024
            }
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                error_msg = f"Grok API error: {response.status_code} - {response.text}"
                if self.logger:
                    self.logger.log(error_msg, "Error")
                return f"Error: {error_msg}"
            
            response_data = response.json()
            assistant_response = response_data["choices"][0]["message"]["content"]
            self.conversation_history.append(
                {"role": "assistant", "content": assistant_response}
            )
            return assistant_response
        except Exception as e:
            if self.logger:
                self.logger.log(f"Error generating response: {str(e)}", "Error")
            self._show_error(f"Grok API error: {str(e)}")
            return f"Error: Could not generate response - {str(e)}"
