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
from tkinter import ttk, messagebox

class GUIComponents:
    """Helper class for creating and managing GUI components."""
    
    @staticmethod
    def create_labeled_frame(parent, title, padding=10, fill='x', expand=False):
        """Create a labeled frame.
        
        Args:
            parent: The parent widget
            title: The frame title
            padding: The padding around the frame
            fill: Fill strategy ('x', 'y', 'both', or 'none')
            expand: Whether to expand to fill available space
            
        Returns:
            The created frame
        """
        frame = ttk.LabelFrame(parent, text=title, padding=padding)
        frame.pack(fill=fill, padx=10, pady=5, expand=expand)
        return frame
    
    @staticmethod
    def create_combobox(parent, state="readonly"):
        """Create a combobox.
        
        Args:
            parent: The parent widget
            state: The combobox state
            
        Returns:
            The created combobox
        """
        combo = ttk.Combobox(parent, state=state)
        combo.pack(fill='x')
        return combo
    
    @staticmethod
    def create_button(parent, text, command, side='top', padx=0, pady=0, state='normal'):
        """Create a button.
        
        Args:
            parent: The parent widget
            text: The button text
            command: The button command
            side: The side to pack the button
            padx: The horizontal padding
            pady: The vertical padding
            state: The button state
            
        Returns:
            The created button
        """
        button = ttk.Button(parent, text=text, command=command, state=state)
        button.pack(side=side, padx=padx, pady=pady)
        return button
    
    @staticmethod
    def create_text_widget(parent, height=20, wrap='word'):
        """Create a text widget.
        
        Args:
            parent: The parent widget
            height: The height of the text widget
            wrap: The text wrapping mode
            
        Returns:
            The created text widget
        """
        text = tk.Text(parent, height=height, wrap=wrap)
        text.pack(fill='both', expand=True)
        return text
    
    @staticmethod
    def create_label(parent, text, side='top', padx=0, pady=0):
        """Create a label.
        
        Args:
            parent: The parent widget
            text: The label text
            side: The side to pack the label
            padx: The horizontal padding
            pady: The vertical padding
            
        Returns:
            The created label
        """
        label = ttk.Label(parent, text=text)
        label.pack(side=side, padx=padx, pady=pady)
        return label
    
    @staticmethod
    def create_context_viewer(parent, conversation_history, title="Conversation Context"):
        """Create a window to view conversation context.
        
        Args:
            parent: The parent widget
            conversation_history: The conversation history to display
            title: The window title
        """
        context_window = tk.Toplevel(parent)
        context_window.title(title)
        context_window.geometry("500x600")
        
        context_text = tk.Text(context_window, wrap='word', padx=10, pady=10)
        context_text.pack(fill='both', expand=True)
        
        for msg in conversation_history:
            role = msg["role"].capitalize()
            content = msg["content"]
            context_text.insert('end', f"{role}: {content}\n\n")
        
        context_text.config(state='disabled')
        
        # Add copy button
        def copy_to_clipboard():
            context_window.clipboard_clear()
            context_window.clipboard_append(context_text.get(1.0, 'end-1c'))
            messagebox.showinfo("Copied", "Context copied to clipboard")
            
        copy_btn = ttk.Button(context_window, text="Copy to Clipboard", command=copy_to_clipboard)
        copy_btn.pack(pady=10)
