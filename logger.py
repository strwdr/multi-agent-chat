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

import tkinter as tk
import datetime

class GUILogger:
    """Logger class that writes to a tkinter Text widget."""
    
    def __init__(self, text_widget):
        """Initialize the logger with a tkinter Text widget.
        
        Args:
            text_widget: A tkinter Text widget where logs will be displayed
        """
        self.text_widget = text_widget
        self.initialized = False
    
    def log(self, message, source="System"):
        """Log a message to the text widget.
        
        Args:
            message: The message to log
            source: The source of the message (default: "System")
        """
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {source}: {message}\n"
        self.text_widget.insert('end', formatted_message)
        self.text_widget.see('end')
        
        # Mark as initialized after first log message
        if not self.initialized:
            self.initialized = True
    
    def clear(self):
        """Clear all logs from the text widget."""
        self.text_widget.delete(1.0, 'end')
        self.log("Log cleared")
