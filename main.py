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
import platform
import os
import time
import threading
import dotenv
from logger import GUILogger
from api_factory import APIFactory
from gui_components import GUIComponents

class DualAgentChatGUI:
    """Main application class for the Dual Agent Chat GUI."""
    
    def __init__(self, root):
        """Initialize the application.
        
        Args:
            root: The tkinter root window
        """
        self.root = root
        self.root.title("Multi Agent Chat")
        self.root.geometry("800x800")
        
        # Load environment variables
        dotenv.load_dotenv()
        
        # Initialize logger to None first
        self.logger = None
        
        # State variables
        self.conversation_started = False
        self.conversation_thread = None
        self.stop_conversation = False
        self.max_turns = 10
        self.current_turn = 0
        self.turn_delay = 2  # seconds between turns
        self.default_prompt = "Hello, let's have a conversation."
        self.default_system_prompt1 = "You are a helpful AI assistant."
        self.default_system_prompt2 = "You are a helpful AI assistant."
        self.ollama_address = os.getenv("OLLAMA_ADDRESS", "http://localhost:11434")
        self.agent1_name = "Agent 1"
        self.agent2_name = "Agent 2"
        self.api_type1 = os.getenv("DEFAULT_API_TYPE1", "ollama")
        self.api_type2 = os.getenv("DEFAULT_API_TYPE2", "ollama")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.grok_api_key = os.getenv("GROK_API_KEY", "")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        
        # Setup GUI components
        self.setup_gui()
        
        # Initialize handlers for two agents with appropriate parameters
        kwargs1 = {}
        kwargs2 = {}
        
        if self.api_type1 == "ollama":
            kwargs1["address"] = self.ollama_address
        elif self.api_type1 == "openai":
            kwargs1["api_key"] = self.openai_api_key
        elif self.api_type1 == "anthropic":
            kwargs1["api_key"] = self.anthropic_api_key
        elif self.api_type1 == "grok":
            kwargs1["api_key"] = self.grok_api_key
        elif self.api_type1 == "gemini":
            kwargs1["api_key"] = self.gemini_api_key
            
        if self.api_type2 == "ollama":
            kwargs2["address"] = self.ollama_address
        elif self.api_type2 == "openai":
            kwargs2["api_key"] = self.openai_api_key
        elif self.api_type2 == "anthropic":
            kwargs2["api_key"] = self.anthropic_api_key
        elif self.api_type2 == "grok":
            kwargs2["api_key"] = self.grok_api_key
        elif self.api_type2 == "gemini":
            kwargs2["api_key"] = self.gemini_api_key
        
        self.agent1 = APIFactory.create_handler(self.api_type1, self.logger, **kwargs1)
        self.agent2 = APIFactory.create_handler(self.api_type2, self.logger, **kwargs2)
        
        # Load initial data
        self.refresh_models()

    def setup_gui(self):
        """Set up the GUI components."""
        # Create main notebook with tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        
        # Create Conversation tab
        self.conversation_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.conversation_frame, text="Conversation")
        
        # Setup the settings tab
        self.setup_settings_tab()
        
        # Setup the conversation tab
        self.setup_conversation_tab()
        
        # Initialize logger
        self.logger = GUILogger(self.log_text)
    
    def setup_settings_tab(self):
        """Set up the settings tab with Ollama settings for both agents."""
        # Create frames for Ollama settings
        settings_label = ttk.Label(self.settings_frame, text="Configure your agents", font=("TkDefaultFont", 12))
        settings_label.pack(pady=10)
        
        # API Connection Settings
        connection_frame = GUIComponents.create_labeled_frame(self.settings_frame, "API Connection Settings")
        
        # API Type Selection for Agent 1
        api_type_frame1 = ttk.Frame(connection_frame)
        api_type_frame1.pack(fill='x', pady=5)
        
        api_type_label1 = ttk.Label(api_type_frame1, text="Agent 1 API Type:")
        api_type_label1.pack(side='left')
        
        self.api_type_combo1 = ttk.Combobox(api_type_frame1, values=["ollama", "openai", "anthropic", "grok", "gemini"], state="readonly")
        self.api_type_combo1.pack(side='left', padx=5)
        self.api_type_combo1.set(self.api_type1)
        self.api_type_combo1.bind("<<ComboboxSelected>>", lambda e: self.update_api_settings_visibility())
        
        # API Type Selection for Agent 2
        api_type_frame2 = ttk.Frame(connection_frame)
        api_type_frame2.pack(fill='x', pady=5)
        
        api_type_label2 = ttk.Label(api_type_frame2, text="Agent 2 API Type:")
        api_type_label2.pack(side='left')
        
        self.api_type_combo2 = ttk.Combobox(api_type_frame2, values=["ollama", "openai", "anthropic", "grok", "gemini"], state="readonly")
        self.api_type_combo2.pack(side='left', padx=5)
        self.api_type_combo2.set(self.api_type2)
        self.api_type_combo2.bind("<<ComboboxSelected>>", lambda e: self.update_api_settings_visibility())
        
        # Ollama API Address
        self.ollama_frame = ttk.Frame(connection_frame)
        self.ollama_frame.pack(fill='x', pady=5)
        
        address_label = ttk.Label(self.ollama_frame, text="Ollama API Address:")
        address_label.pack(side='left')
        
        self.address_entry = ttk.Entry(self.ollama_frame, width=30)
        self.address_entry.pack(side='left', padx=5, fill='x', expand=True)
        self.address_entry.insert(0, self.ollama_address)
        
        # OpenAI API Key
        self.openai_frame = ttk.Frame(connection_frame)
        
        openai_key_label = ttk.Label(self.openai_frame, text="OpenAI API Key:")
        openai_key_label.pack(side='left')
        
        self.openai_key_entry = ttk.Entry(self.openai_frame, width=40, show="*")
        self.openai_key_entry.pack(side='left', padx=5, fill='x', expand=True)
        # Display masked key if it exists
        if self.openai_api_key:
            self.openai_key_entry.insert(0, "*" * 12)
        else:
            self.openai_key_entry.insert(0, "")
        
        # Anthropic API Key
        self.anthropic_frame = ttk.Frame(connection_frame)
        
        anthropic_key_label = ttk.Label(self.anthropic_frame, text="Anthropic API Key:")
        anthropic_key_label.pack(side='left')
        
        self.anthropic_key_entry = ttk.Entry(self.anthropic_frame, width=40, show="*")
        self.anthropic_key_entry.pack(side='left', padx=5, fill='x', expand=True)
        # Display masked key if it exists
        if self.anthropic_api_key:
            self.anthropic_key_entry.insert(0, "*" * 12)
        else:
            self.anthropic_key_entry.insert(0, "")
            
        # Grok API Key
        self.grok_frame = ttk.Frame(connection_frame)
        
        grok_key_label = ttk.Label(self.grok_frame, text="Grok API Key:")
        grok_key_label.pack(side='left')
        
        self.grok_key_entry = ttk.Entry(self.grok_frame, width=40, show="*")
        self.grok_key_entry.pack(side='left', padx=5, fill='x', expand=True)
        # Display masked key if it exists
        if hasattr(self, 'grok_api_key') and self.grok_api_key:
            self.grok_key_entry.insert(0, "*" * 12)
        else:
            self.grok_key_entry.insert(0, "")
            
        # Gemini API Key
        self.gemini_frame = ttk.Frame(connection_frame)
        
        gemini_key_label = ttk.Label(self.gemini_frame, text="Gemini API Key:")
        gemini_key_label.pack(side='left')
        
        self.gemini_key_entry = ttk.Entry(self.gemini_frame, width=40, show="*")
        self.gemini_key_entry.pack(side='left', padx=5, fill='x', expand=True)
        # Display masked key if it exists
        if hasattr(self, 'gemini_api_key') and self.gemini_api_key:
            self.gemini_key_entry.insert(0, "*" * 12)
        else:
            self.gemini_key_entry.insert(0, "")
        
        # Apply API Settings button
        self.apply_api_btn = GUIComponents.create_button(
            connection_frame, "Apply API Settings", self.apply_api_settings, pady=5
        )
        
        # Initialize API settings visibility
        self.update_api_settings_visibility()
        
        # Agent 1 Settings Section
        agent1_frame = GUIComponents.create_labeled_frame(self.settings_frame, "Agent 1 Settings")
        
        # Agent 1 Name
        name_frame1 = ttk.Frame(agent1_frame)
        name_frame1.pack(fill='x', pady=5)
        
        name_label1 = ttk.Label(name_frame1, text="Agent 1 Name:")
        name_label1.pack(side='left')
        
        self.agent1_name_entry = ttk.Entry(name_frame1, width=20)
        self.agent1_name_entry.pack(side='left', padx=5)
        self.agent1_name_entry.insert(0, self.agent1_name)
        
        # Model Selection for Agent 1
        model_label1 = ttk.Label(agent1_frame, text="Select AI Model for Agent 1:")
        model_label1.pack(anchor='w', pady=(5, 0))
        
        self.model_combo1 = GUIComponents.create_combobox(agent1_frame)
        
        # System Prompt for Agent 1
        system_prompt_label1 = ttk.Label(agent1_frame, text="System Prompt for Agent 1:")
        system_prompt_label1.pack(anchor='w', pady=(10, 0))
        
        self.system_prompt_entry1 = ttk.Entry(agent1_frame, width=50)
        self.system_prompt_entry1.pack(fill='x', pady=5)
        self.system_prompt_entry1.insert(0, self.default_system_prompt1)
        
        # Agent 2 Settings Section
        agent2_frame = GUIComponents.create_labeled_frame(self.settings_frame, "Agent 2 Settings")
        
        # Agent 2 Name
        name_frame2 = ttk.Frame(agent2_frame)
        name_frame2.pack(fill='x', pady=5)
        
        name_label2 = ttk.Label(name_frame2, text="Agent 2 Name:")
        name_label2.pack(side='left')
        
        self.agent2_name_entry = ttk.Entry(name_frame2, width=20)
        self.agent2_name_entry.pack(side='left', padx=5)
        self.agent2_name_entry.insert(0, self.agent2_name)
        
        # Model Selection for Agent 2
        model_label2 = ttk.Label(agent2_frame, text="Select AI Model for Agent 2:")
        model_label2.pack(anchor='w', pady=(5, 0))
        
        self.model_combo2 = GUIComponents.create_combobox(agent2_frame)
        
        # System Prompt for Agent 2
        system_prompt_label2 = ttk.Label(agent2_frame, text="System Prompt for Agent 2:")
        system_prompt_label2.pack(anchor='w', pady=(10, 0))
        
        self.system_prompt_entry2 = ttk.Entry(agent2_frame, width=50)
        self.system_prompt_entry2.pack(fill='x', pady=5)
        self.system_prompt_entry2.insert(0, self.default_system_prompt2)
        
        # Refresh models button
        self.refresh_models_btn = GUIComponents.create_button(
            self.settings_frame, "Refresh Models", self.refresh_models, pady=5
        )
        
        # Conversation Settings Section
        self.conversation_settings_frame = GUIComponents.create_labeled_frame(self.settings_frame, "Conversation Settings")
        
        # Initial prompt
        prompt_label = ttk.Label(self.conversation_settings_frame, text=f"Initial Prompt (from {self.agent1_name}):")
        prompt_label.pack(anchor='w', pady=(5, 0))
        
        self.initial_prompt_entry = ttk.Entry(self.conversation_settings_frame, width=50)
        self.initial_prompt_entry.pack(fill='x', pady=5)
        self.initial_prompt_entry.insert(0, self.default_prompt)
        
        # Max turns
        turns_frame = ttk.Frame(self.conversation_settings_frame)
        turns_frame.pack(fill='x', pady=5)
        
        turns_label = ttk.Label(turns_frame, text="Maximum Turns:")
        turns_label.pack(side='left')
        
        self.turns_spinbox = ttk.Spinbox(turns_frame, from_=1, to=50, width=5)
        self.turns_spinbox.pack(side='left', padx=5)
        self.turns_spinbox.set(self.max_turns)
        
        # Delay between turns
        delay_frame = ttk.Frame(self.conversation_settings_frame)
        delay_frame.pack(fill='x', pady=5)
        
        delay_label = ttk.Label(delay_frame, text="Delay Between Turns (seconds):")
        delay_label.pack(side='left')
        
        self.delay_spinbox = ttk.Spinbox(delay_frame, from_=0, to=10, increment=0.5, width=5)
        self.delay_spinbox.pack(side='left', padx=5)
        self.delay_spinbox.set(self.turn_delay)
    
    def setup_conversation_tab(self):
        """Set up the conversation tab with logs and controls."""
        # Conversation controls
        controls_frame = ttk.Frame(self.conversation_frame)
        controls_frame.pack(fill='x', pady=10)
        
        # Start/Stop conversation button
        self.start_conv_btn = GUIComponents.create_button(
            controls_frame, "Start Conversation", self.start_conversation, 
            side='left', padx=5
        )
        
        # Context management
        context_frame = ttk.Frame(controls_frame)
        context_frame.pack(side='right')
        
        self.view_context1_btn = GUIComponents.create_button(
            context_frame, f"View {self.agent1_name} Context", self.view_context1, side='left', padx=5
        )
        
        self.view_context2_btn = GUIComponents.create_button(
            context_frame, f"View {self.agent2_name} Context", self.view_context2, side='left', padx=5
        )
        
        self.clear_context_btn = GUIComponents.create_button(
            context_frame, "Clear Contexts", self.clear_context, side='left'
        )
        
        # Context length indicator
        context_info_frame = ttk.Frame(self.conversation_frame)
        context_info_frame.pack(fill='x', pady=(0, 5))
        
        self.context_length_label1 = ttk.Label(context_info_frame, text=f"{self.agent1_name}: 0 messages")
        self.context_length_label1.pack(side='left', padx=(0, 10))
        
        self.context_length_label2 = ttk.Label(context_info_frame, text=f"{self.agent2_name}: 0 messages")
        self.context_length_label2.pack(side='left')
        
        # Turn counter
        self.turn_label = ttk.Label(context_info_frame, text="Turn: 0/0")
        self.turn_label.pack(side='right', padx=10)
        
        # Clear logs button
        self.clear_logs_btn = GUIComponents.create_button(
            context_info_frame, "Clear Logs", self.clear_logs, side='right'
        )
        
        # Create a frame to hold both log and conversation windows side by side
        content_frame = ttk.Frame(self.conversation_frame)
        content_frame.pack(fill='both', expand=True, pady=5)
        
        # Message log (left side)
        log_frame = ttk.LabelFrame(content_frame, text="Conversation Log")
        log_frame.pack(fill='both', expand=True, pady=5, side='left', padx=(0, 5))
        
        self.log_text = GUIComponents.create_text_widget(log_frame)
        
        # Clean conversation window (right side)
        conv_frame = ttk.LabelFrame(content_frame, text="Clean Conversation (Copy/Paste)")
        conv_frame.pack(fill='both', expand=True, pady=5, side='right', padx=(5, 0))
        
        # Create a frame for the conversation text and copy button
        conv_content_frame = ttk.Frame(conv_frame)
        conv_content_frame.pack(fill='both', expand=True)
        
        self.conv_text = GUIComponents.create_text_widget(conv_content_frame)
        
        # Add copy button for conversation
        copy_frame = ttk.Frame(conv_frame)
        copy_frame.pack(fill='x', pady=(0, 5))
        
        self.copy_conv_btn = GUIComponents.create_button(
            copy_frame, "Copy Conversation to Clipboard", self.copy_conversation_to_clipboard, 
            side='right', padx=5
        )
        
    # ===== UI Action Methods =====
    
    def update_api_settings_visibility(self):
        """Update the visibility of API settings based on selected API types."""
        api_type1 = self.api_type_combo1.get()
        api_type2 = self.api_type_combo2.get()
        
        # Hide all frames first
        self.ollama_frame.pack_forget()
        self.openai_frame.pack_forget()
        self.anthropic_frame.pack_forget()
        self.grok_frame.pack_forget()
        self.gemini_frame.pack_forget()
        
        # Show relevant frames based on selected API types
        if "ollama" in (api_type1, api_type2):
            self.ollama_frame.pack(fill='x', pady=5)
            
        if "openai" in (api_type1, api_type2):
            self.openai_frame.pack(fill='x', pady=5)
            
        if "anthropic" in (api_type1, api_type2):
            self.anthropic_frame.pack(fill='x', pady=5)
            
        if "grok" in (api_type1, api_type2):
            self.grok_frame.pack(fill='x', pady=5)
            
        if "gemini" in (api_type1, api_type2):
            self.gemini_frame.pack(fill='x', pady=5)
    
    def apply_api_settings(self):
        """Apply the API settings."""
        # Get API types
        new_api_type1 = self.api_type_combo1.get()
        new_api_type2 = self.api_type_combo2.get()
        
        # Get Ollama address if needed
        new_ollama_address = ""
        if "ollama" in (new_api_type1, new_api_type2):
            new_ollama_address = self.address_entry.get().strip()
            if not new_ollama_address:
                messagebox.showerror("Error", "Please enter a valid Ollama API address")
                return
                
            # Validate the address format
            if not (new_ollama_address.startswith("http://") or new_ollama_address.startswith("https://")):
                new_ollama_address = "http://" + new_ollama_address
                self.address_entry.delete(0, 'end')
                self.address_entry.insert(0, new_ollama_address)
            
            self.ollama_address = new_ollama_address
        
        # Get API keys if needed
        new_openai_key = ""
        if "openai" in (new_api_type1, new_api_type2):
            new_openai_key = self.openai_key_entry.get().strip()
            # If the key is masked, use the existing key
            if new_openai_key == "*" * 12:
                new_openai_key = self.openai_api_key
            elif not new_openai_key:
                messagebox.showerror("Error", "Please enter a valid OpenAI API key")
                return
            self.openai_api_key = new_openai_key
            
        new_anthropic_key = ""
        if "anthropic" in (new_api_type1, new_api_type2):
            new_anthropic_key = self.anthropic_key_entry.get().strip()
            # If the key is masked, use the existing key
            if new_anthropic_key == "*" * 12:
                new_anthropic_key = self.anthropic_api_key
            elif not new_anthropic_key:
                messagebox.showerror("Error", "Please enter a valid Anthropic API key")
                return
            self.anthropic_api_key = new_anthropic_key
            
        new_grok_key = ""
        if "grok" in (new_api_type1, new_api_type2):
            new_grok_key = self.grok_key_entry.get().strip()
            # If the key is masked, use the existing key
            if new_grok_key == "*" * 12:
                new_grok_key = self.grok_api_key
            elif not new_grok_key:
                messagebox.showerror("Error", "Please enter a valid Grok API key")
                return
            self.grok_api_key = new_grok_key
            
        new_gemini_key = ""
        if "gemini" in (new_api_type1, new_api_type2):
            new_gemini_key = self.gemini_key_entry.get().strip()
            # If the key is masked, use the existing key
            if new_gemini_key == "*" * 12:
                new_gemini_key = self.gemini_api_key
            elif not new_gemini_key:
                messagebox.showerror("Error", "Please enter a valid Gemini API key")
                return
            self.gemini_api_key = new_gemini_key
        
        # Update API types
        self.api_type1 = new_api_type1
        self.api_type2 = new_api_type2
        
        # Create new API handlers
        kwargs1 = {}
        kwargs2 = {}
        
        if new_api_type1 == "ollama":
            kwargs1["address"] = new_ollama_address
        elif new_api_type1 == "openai":
            kwargs1["api_key"] = new_openai_key
        elif new_api_type1 == "anthropic":
            kwargs1["api_key"] = new_anthropic_key
        elif new_api_type1 == "grok":
            kwargs1["api_key"] = new_grok_key
        elif new_api_type1 == "gemini":
            kwargs1["api_key"] = new_gemini_key
            
        if new_api_type2 == "ollama":
            kwargs2["address"] = new_ollama_address
        elif new_api_type2 == "openai":
            kwargs2["api_key"] = new_openai_key
        elif new_api_type2 == "anthropic":
            kwargs2["api_key"] = new_anthropic_key
        elif new_api_type2 == "grok":
            kwargs2["api_key"] = new_grok_key
        elif new_api_type2 == "gemini":
            kwargs2["api_key"] = new_gemini_key
        
        self.agent1 = APIFactory.create_handler(new_api_type1, self.logger, **kwargs1)
        self.agent2 = APIFactory.create_handler(new_api_type2, self.logger, **kwargs2)
        
        # Log the changes
        self.logger.log(f"Updated Agent 1 to use {new_api_type1} API", "System")
        self.logger.log(f"Updated Agent 2 to use {new_api_type2} API", "System")
        
        # Refresh models to test the connection - do this separately for each agent
        # Get models for agent 1
        models1 = self.agent1.get_available_models()
        self.model_combo1['values'] = models1
        if models1:
            self.model_combo1.set(models1[0])
            
        # Get models for agent 2
        models2 = self.agent2.get_available_models()
        self.model_combo2['values'] = models2
        if models2:
            # Try to set a different model for agent 2 if available
            if len(models2) > 1:
                self.model_combo2.set(models2[1])
            else:
                self.model_combo2.set(models2[0])
    
    def refresh_models(self):
        """Refresh the list of available models for both agents."""
        # Get models for agent 1
        try:
            models1 = self.agent1.get_available_models()
            self.model_combo1['values'] = models1
            if models1:
                self.model_combo1.set(models1[0])
        except Exception as e:
            self.logger.log(f"Error loading models for Agent 1: {str(e)}", "Error")
            
        # Get models for agent 2
        try:
            models2 = self.agent2.get_available_models()
            self.model_combo2['values'] = models2
            if models2:
                # Try to set a different model for agent 2 if available
                if len(models2) > 1:
                    self.model_combo2.set(models2[1])
                else:
                    self.model_combo2.set(models2[0])
        except Exception as e:
            self.logger.log(f"Error loading models for Agent 2: {str(e)}", "Error")
    
    def start_conversation(self):
        """Start or stop the conversation between the two agents."""
        if not self.conversation_started:
            # Get selected models and set them
            model1 = self.model_combo1.get()
            model2 = self.model_combo2.get()
            
            if not model1 or not model2:
                messagebox.showerror("Error", "Please select models for both agents")
                return
                
            self.agent1.set_model(model1)
            self.agent2.set_model(model2)
            
            # Set system prompts
            system_prompt1 = self.system_prompt_entry1.get()
            system_prompt2 = self.system_prompt_entry2.get()
            self.agent1.set_system_prompt(system_prompt1)
            self.agent2.set_system_prompt(system_prompt2)
            
            # Get agent names
            self.agent1_name = self.agent1_name_entry.get() or "Agent 1"
            self.agent2_name = self.agent2_name_entry.get() or "Agent 2"
            
            # Update UI elements that reference agent names
            self.view_context1_btn.config(text=f"View {self.agent1_name} Context")
            self.view_context2_btn.config(text=f"View {self.agent2_name} Context")
            
            # Update the initial prompt label
            for widget in self.conversation_settings_frame.winfo_children():
                if isinstance(widget, ttk.Label) and "Initial Prompt" in widget.cget("text"):
                    widget.config(text=f"Initial Prompt (from {self.agent1_name}):")
                    break
            
            # Get conversation settings
            try:
                self.max_turns = int(self.turns_spinbox.get())
                self.turn_delay = float(self.delay_spinbox.get())
            except ValueError:
                messagebox.showerror("Error", "Invalid values for turns or delay")
                return
            
            # Clear previous conversation
            if self.logger and self.logger.text_widget.get(1.0, 'end').strip():
                if not messagebox.askyesno("Start New Conversation", 
                                         "Starting a new conversation will clear the current logs. Continue?"):
                    return
                    
            self.agent1.clear_conversation_history()
            self.agent2.clear_conversation_history()
            self.clear_logs(confirm=False)
            
            # Start conversation
            self.conversation_started = True
            self.stop_conversation = False
            self.current_turn = 0
            self.start_conv_btn.config(text="Stop Conversation")
            
            # Switch to conversation tab
            self.notebook.select(1)  # Select the conversation tab (index 1)
            
            # Start conversation in a separate thread
            self.conversation_thread = threading.Thread(target=self.run_conversation)
            self.conversation_thread.daemon = True
            self.conversation_thread.start()
        else:
            # Stop conversation
            self.stop_conversation = True
            self.conversation_started = False
            self.start_conv_btn.config(text="Start Conversation")
            self.logger.log("Conversation stopped by user", "System")
    
    def run_conversation(self):
        """Run the conversation between the two agents."""
        try:
            # Clear the clean conversation window
            self.conv_text.delete(1.0, 'end')
            
            # Get the initial prompt
            initial_prompt = self.initial_prompt_entry.get()
            self.logger.log(f"Starting conversation with initial prompt: {initial_prompt}", "System")
            
            # Add initial prompt to clean conversation with clear indication it's the initial prompt
            self.conv_text.insert('end', f"[Initial Prompt]\n{initial_prompt}\n\n")
            
            # Inject the initial prompt as if it were a response from Agent 1
            # This way Agent 2 can respond to it naturally
            self.agent1.conversation_history.append({"role": "assistant", "content": initial_prompt})
            
            # Initialize response2 variable before the loop
            response2 = initial_prompt
            
            # Run for the specified number of turns
            for turn in range(1, self.max_turns + 1):
                if self.stop_conversation:
                    break
                    
                self.current_turn = turn
                self.update_turn_counter()
                
                # Agent 2 responds to Agent 1's message
                agent1_display = f"{self.agent1_name} ({self.agent1.selected_model})"
                self.logger.log(response2, agent1_display)
                response1 = self.agent2.get_response(response2)
                
                # Add to clean conversation
                self.conv_text.insert('end', f"{self.agent2_name}: {response1}\n\n")
                self.conv_text.see('end')
                
                # Update UI
                self.update_context_length()
                time.sleep(self.turn_delay)
                
                if self.stop_conversation or turn == self.max_turns:
                    break
                
                # Agent 1 responds to Agent 2's message
                agent2_display = f"{self.agent2_name} ({self.agent2.selected_model})"
                self.logger.log(response1, agent2_display)
                response2 = self.agent1.get_response(response1)
                
                # Add to clean conversation
                self.conv_text.insert('end', f"{self.agent1_name}: {response2}\n\n")
                self.conv_text.see('end')
                
                # Update UI
                self.update_context_length()
                time.sleep(self.turn_delay)
            
            if not self.stop_conversation:
                self.logger.log("Conversation completed (reached maximum turns)", "System")
                self.conversation_started = False
                self.root.after(0, lambda: self.start_conv_btn.config(text="Start Conversation"))
                
        except Exception as e:
            self.logger.log(f"Error in conversation: {str(e)}", "Error")
            self.conversation_started = False
            self.root.after(0, lambda: self.start_conv_btn.config(text="Start Conversation"))
    
    def update_turn_counter(self):
        """Update the turn counter display."""
        self.root.after(0, lambda: self.turn_label.config(text=f"Turn: {self.current_turn}/{self.max_turns}"))
    
    def view_context1(self):
        """View Agent 1's conversation context."""
        history = self.agent1.get_conversation_history()
        GUIComponents.create_context_viewer(self.root, history, f"{self.agent1_name} Context")
    
    def view_context2(self):
        """View Agent 2's conversation context."""
        history = self.agent2.get_conversation_history()
        GUIComponents.create_context_viewer(self.root, history, f"{self.agent2_name} Context")
    
    def clear_context(self):
        """Clear both agents' conversation contexts."""
        if messagebox.askyesno("Clear Contexts", 
                             "Are you sure you want to clear both conversation contexts?"):
            self.agent1.clear_conversation_history()
            self.agent2.clear_conversation_history()
            self.update_context_length()
    
    def update_context_length(self):
        """Update the context length displays."""
        count1 = self.agent1.get_conversation_length()
        count2 = self.agent2.get_conversation_length()
        self.root.after(0, lambda: self.context_length_label1.config(text=f"{self.agent1_name}: {count1} messages"))
        self.root.after(0, lambda: self.context_length_label2.config(text=f"{self.agent2_name}: {count2} messages"))
    
    def copy_conversation_to_clipboard(self):
        """Copy the clean conversation to clipboard."""
        conversation_text = self.conv_text.get(1.0, 'end-1c')
        if conversation_text.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(conversation_text)
            messagebox.showinfo("Copied", "Conversation copied to clipboard")
        else:
            messagebox.showinfo("Empty Conversation", "There is no conversation to copy")
    
    def clear_logs(self, confirm=True):
        """Clear the message logs and conversation window.
        
        Args:
            confirm: Whether to show a confirmation dialog
        """
        if not confirm or messagebox.askyesno("Clear Logs", "Are you sure you want to clear the message log?"):
            self.logger.clear()
            self.conv_text.delete(1.0, 'end')

if __name__ == "__main__":
    root = tk.Tk()
    app = DualAgentChatGUI(root)
    root.mainloop()
