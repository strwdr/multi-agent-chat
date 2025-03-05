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

from ollama_handler import OllamaHandler
from openai_handler import OpenAIHandler
from anthropic_handler import AnthropicHandler
from grok_handler import GrokHandler
from gemini_handler import GeminiHandler

class APIFactory:
    """Factory class for creating API handlers."""
    
    @staticmethod
    def create_handler(api_type, logger, **kwargs):
        """Create an API handler of the specified type.
        
        Args:
            api_type: The type of API handler to create ('ollama', 'openai', 'anthropic', 'grok', 'gemini')
            logger: The logger instance
            **kwargs: Additional arguments to pass to the handler constructor
            
        Returns:
            An instance of the specified API handler
        """
        if api_type.lower() == 'ollama':
            address = kwargs.get('address', 'http://localhost:11434')
            return OllamaHandler(logger, address)
        elif api_type.lower() == 'openai':
            api_key = kwargs.get('api_key', None)
            return OpenAIHandler(logger, api_key)
        elif api_type.lower() == 'anthropic':
            api_key = kwargs.get('api_key', None)
            return AnthropicHandler(logger, api_key)
        elif api_type.lower() == 'grok':
            api_key = kwargs.get('api_key', None)
            return GrokHandler(logger, api_key)
        elif api_type.lower() == 'gemini':
            api_key = kwargs.get('api_key', None)
            return GeminiHandler(logger, api_key)
        else:
            raise ValueError(f"Unknown API type: {api_type}")
