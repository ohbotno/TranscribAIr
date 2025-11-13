"""
Feedback panel component for displaying organized feedback.
Reusable component for both Record and Upload tabs.
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Optional, Callable
from pathlib import Path
import threading

from core.feedback import OrganizedFeedback, StructuredFeedback, FeedbackOrganizer
from core.export import FeedbackExporter
from core.rubric import Rubric, RubricManager
from core.settings import SettingsManager
from ui.rubric_dialog import RubricSelectorDialog


class FeedbackPanel(ctk.CTkFrame):
    """Panel for displaying and managing organized feedback."""

    # Class variable to track all FeedbackPanel instances
    _all_instances = []

    def __init__(
        self,
        parent,
        rubric_manager: RubricManager,
        settings_manager: SettingsManager,
        feedback_organizer: FeedbackOrganizer
    ):
        super().__init__(parent)

        self.rubric_manager = rubric_manager
        self.settings_manager = settings_manager
        self.feedback_organizer = feedback_organizer
        self.current_feedback: Optional[OrganizedFeedback] = None
        self.current_rubric: Optional[Rubric] = None
        self.current_transcript: str = ""
        self.selected_provider: Optional[str] = None  # Override provider

        self._create_ui()
        self._initialize_provider_dropdown()
        self._load_last_rubric()

        # Register this instance
        FeedbackPanel._all_instances.append(self)

    def _create_ui(self):
        """Create feedback panel UI."""
        # Header with simplified controls
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=5, pady=5)

        # Left side - Rubric info and word count
        left_info = ctk.CTkFrame(header, fg_color="transparent")
        left_info.pack(side="left", padx=10)

        self.rubric_label = ctk.CTkLabel(
            left_info,
            text="No rubric selected",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.rubric_label.pack(anchor="w")

        self.word_count_label = ctk.CTkLabel(
            left_info,
            text="",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.word_count_label.pack(anchor="w")

        # Control buttons (right side)
        button_container = ctk.CTkFrame(header)
        button_container.pack(side="right", padx=10)

        # Font size controls
        font_frame = ctk.CTkFrame(button_container, fg_color="transparent")
        font_frame.pack(side="left", padx=5)

        ctk.CTkLabel(
            font_frame,
            text="Font:",
            font=ctk.CTkFont(size=10)
        ).pack(side="left", padx=2)

        self.current_font_size = 12  # Default font size

        self.font_decrease_btn = ctk.CTkButton(
            font_frame,
            text="-",
            command=lambda: self._adjust_font_size(-1),
            width=30,
            height=28
        )
        self.font_decrease_btn.pack(side="left", padx=1)

        self.font_size_label = ctk.CTkLabel(
            font_frame,
            text="12",
            font=ctk.CTkFont(size=10),
            width=25
        )
        self.font_size_label.pack(side="left", padx=2)

        self.font_increase_btn = ctk.CTkButton(
            font_frame,
            text="+",
            command=lambda: self._adjust_font_size(1),
            width=30,
            height=28
        )
        self.font_increase_btn.pack(side="left", padx=1)

        self.rubric_btn = ctk.CTkButton(
            button_container,
            text="Select Rubric",
            command=self._select_rubric,
            width=110,
            height=32
        )
        self.rubric_btn.pack(side="left", padx=2)

        self.organize_btn = ctk.CTkButton(
            button_container,
            text="Organize",
            command=self._organize_feedback,
            width=90,
            height=32,
            state="disabled"
        )
        self.organize_btn.pack(side="left", padx=2)

        # Feedback mode selector
        self.mode_var = ctk.StringVar(value="")
        self.mode_dropdown = ctk.CTkOptionMenu(
            button_container,
            variable=self.mode_var,
            values=["Organized", "Structured"],
            width=110,
            height=32
        )
        self.mode_dropdown.pack(side="left", padx=2)

        # Provider selection dropdown
        self.provider_var = ctk.StringVar(value="")
        self.provider_dropdown = ctk.CTkOptionMenu(
            button_container,
            variable=self.provider_var,
            values=["Ollama", "OpenAI", "Anthropic", "OpenRouter"],
            width=120,
            height=32,
            command=self._on_provider_changed
        )
        self.provider_dropdown.pack(side="left", padx=2)

        # Export button (simplified - defaults to clipboard)
        self.export_btn = ctk.CTkButton(
            button_container,
            text="📋 Copy Feedback",
            command=lambda: self._export_feedback("Copy to Clipboard"),
            width=130,
            height=32,
            state="disabled"
        )
        self.export_btn.pack(side="left", padx=2)

        # More export options dropdown
        export_options = ["Save as Text", "Save as Markdown", "Save as PDF", "Save as Word"]
        self.export_var = ctk.StringVar(value="More...")
        self.export_dropdown = ctk.CTkOptionMenu(
            button_container,
            variable=self.export_var,
            values=export_options,
            command=self._export_feedback,
            width=90,
            height=32,
            state="disabled"
        )
        self.export_dropdown.pack(side="left", padx=2)

        # Feedback display - scrollable frame with sections
        self.feedback_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=("gray95", "gray20")
        )
        self.feedback_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Initial placeholder
        self.placeholder_label = ctk.CTkLabel(
            self.feedback_scroll,
            text="Select a rubric and transcribe audio to organize feedback.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.placeholder_label.pack(pady=50)

        # Transcript drawer toggle and drawer frame
        self.transcript_visible = False
        self.transcript_drawer = None

        # Toggle button at bottom
        toggle_frame = ctk.CTkFrame(self)
        toggle_frame.pack(fill="x", padx=5, pady=(0, 5))

        self.transcript_toggle_btn = ctk.CTkButton(
            toggle_frame,
            text="▲ Show Raw Transcript",
            command=self._toggle_transcript,
            width=180,
            height=28,
            fg_color="gray60",
            state="disabled"
        )
        self.transcript_toggle_btn.pack(pady=2)

    def _initialize_provider_dropdown(self):
        """Initialize provider and mode with settings default."""
        settings = self.settings_manager.load_settings()
        provider_map = {
            "ollama": "Ollama",
            "openai": "OpenAI",
            "anthropic": "Anthropic",
            "openrouter": "OpenRouter"
        }
        default_provider = provider_map.get(settings.llm.provider, "Ollama")
        self.provider_var.set(default_provider)
        self.selected_provider = settings.llm.provider

        # Initialize mode selector
        mode_map = {
            "organized": "Organized",
            "structured": "Structured"
        }
        default_mode = mode_map.get(settings.feedback.feedback_mode, "Organized")
        self.mode_var.set(default_mode)

    def _on_provider_changed(self, choice: str):
        """Handle provider selection change."""
        provider_map = {
            "Ollama": "ollama",
            "OpenAI": "openai",
            "Anthropic": "anthropic",
            "OpenRouter": "openrouter"
        }
        self.selected_provider = provider_map.get(choice, "ollama")

    def _adjust_font_size(self, delta: int):
        """Adjust feedback display font size."""
        self.current_font_size = max(8, min(24, self.current_font_size + delta))
        self.font_size_label.configure(text=str(self.current_font_size))

        # Re-display feedback with new font size if feedback exists
        if self.current_feedback:
            self._display_feedback(self.current_feedback)

    def _calculate_word_count(self, feedback) -> int:
        """Calculate word count for feedback."""
        if isinstance(feedback, OrganizedFeedback):
            text = feedback.summary + " " + " ".join(feedback.criterion_feedback.values())
        elif isinstance(feedback, StructuredFeedback):
            text = feedback.feedback_text
        else:
            text = str(feedback)

        return len(text.split())

    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()  # Required for clipboard to work

    def _clean_markdown(self, text: str) -> str:
        """Remove markdown formatting for clean display."""
        import re

        # Remove markdown headers (### Header -> Header)
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)

        # Remove bold/italic markers (** or __ or *)
        text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', text)  # Bold+italic
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)      # Bold
        text = re.sub(r'__(.+?)__', r'\1', text)          # Bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)          # Italic
        text = re.sub(r'_(.+?)_', r'\1', text)            # Italic

        # Remove code blocks (` or ```)
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`(.+?)`', r'\1', text)

        # Remove links [text](url) -> text
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)

        # Remove horizontal rules
        text = re.sub(r'^-{3,}$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^={3,}$', '', text, flags=re.MULTILINE)

        # Remove blockquotes
        text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)

        # Clean up multiple blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    def _toggle_transcript(self):
        """Toggle transcript drawer visibility."""
        if self.transcript_visible:
            # Hide drawer
            if self.transcript_drawer:
                self.transcript_drawer.pack_forget()
            self.transcript_visible = False
            self.transcript_toggle_btn.configure(text="▲ Show Raw Transcript")
        else:
            # Show drawer
            if not self.transcript_drawer:
                # Create drawer frame
                self.transcript_drawer = ctk.CTkFrame(self, height=150)

                drawer_header = ctk.CTkFrame(self.transcript_drawer)
                drawer_header.pack(fill="x", padx=5, pady=2)

                ctk.CTkLabel(
                    drawer_header,
                    text="Raw Transcript",
                    font=ctk.CTkFont(size=11, weight="bold")
                ).pack(side="left", padx=5)

                self.transcript_drawer_text = ctk.CTkTextbox(
                    self.transcript_drawer,
                    font=ctk.CTkFont(size=11),
                    wrap="word",
                    height=120
                )
                self.transcript_drawer_text.pack(fill="both", expand=True, padx=5, pady=2)
                self.transcript_drawer_text.insert("1.0", self.current_transcript)
                self.transcript_drawer_text.configure(state="disabled")

            # Repack in correct order (before toggle button frame)
            self.transcript_drawer.pack(fill="both", expand=False, padx=5, pady=5, before=self.transcript_toggle_btn.master)
            self.transcript_visible = True
            self.transcript_toggle_btn.configure(text="▼ Hide Raw Transcript")

    def set_transcript(self, transcript: str):
        """Set the current transcript for feedback organization."""
        self.current_transcript = transcript
        self._update_organize_button()
        # Enable transcript toggle button
        self.transcript_toggle_btn.configure(state="normal")
        # Update drawer if already open
        if self.transcript_drawer and hasattr(self, 'transcript_drawer_text'):
            self.transcript_drawer_text.configure(state="normal")
            self.transcript_drawer_text.delete("1.0", "end")
            self.transcript_drawer_text.insert("1.0", transcript)
            self.transcript_drawer_text.configure(state="disabled")

    def _update_organize_button(self):
        """Update organize button state based on transcript and rubric availability."""
        if self.current_transcript and self.current_rubric:
            self.organize_btn.configure(state="normal")
        else:
            self.organize_btn.configure(state="disabled")

    def _select_rubric(self):
        """Open rubric selector dialog."""
        dialog = RubricSelectorDialog(
            self,
            self.rubric_manager,
            on_select=self._on_rubric_selected
        )

    def _load_last_rubric(self):
        """Load the last selected rubric from settings."""
        settings = self.settings_manager.load_settings()
        if settings.feedback.last_selected_rubric:
            try:
                # Try to load the rubric
                rubric = self.rubric_manager.load_rubric(settings.feedback.last_selected_rubric)
                if rubric:
                    self.current_rubric = rubric
                    self.rubric_label.configure(
                        text=f"Rubric: {rubric.name} ({len(rubric.criteria)} criteria)",
                        text_color="white"
                    )
                    self._update_organize_button()
            except Exception as e:
                # If rubric can't be loaded, silently continue
                pass

    def _on_rubric_selected(self, rubric: Rubric):
        """Handle rubric selection."""
        self.current_rubric = rubric
        self.rubric_label.configure(
            text=f"Rubric: {rubric.name} ({len(rubric.criteria)} criteria)",
            text_color="white"
        )
        self._update_organize_button()

        # Save as last selected rubric
        self.settings_manager.update_feedback_settings(last_selected_rubric=rubric.name)

        # Sync selection to all other FeedbackPanel instances
        for instance in FeedbackPanel._all_instances:
            if instance != self:  # Don't update self again
                instance._sync_rubric_selection(rubric)

        # Auto-organize if transcript exists and auto-organize is enabled
        settings = self.settings_manager.load_settings()
        if settings.feedback.auto_organize and self.current_transcript:
            self._organize_feedback()

    def _sync_rubric_selection(self, rubric: Rubric):
        """Sync rubric selection from another FeedbackPanel instance."""
        self.current_rubric = rubric
        self.rubric_label.configure(
            text=f"Rubric: {rubric.name} ({len(rubric.criteria)} criteria)",
            text_color="white"
        )
        self._update_organize_button()
        # Don't auto-organize or save to settings - that's already done by the originating panel

    def _organize_feedback(self):
        """Organize feedback using LLM."""
        if not self.current_transcript or not self.current_rubric:
            return

        # Use selected provider or fall back to settings default
        provider_name = self.selected_provider
        if not provider_name:
            settings = self.settings_manager.load_settings()
            provider_name = settings.llm.provider

        # Try to auto-start Ollama if selected
        if provider_name == "ollama":
            self._try_start_ollama()

        # Determine mode (from dropdown or settings)
        mode_map = {"Organized": "organized", "Structured": "structured"}
        selected_mode = mode_map.get(self.mode_var.get(), "organized")

        # Disable button and show progress
        self.organize_btn.configure(state="disabled", text="Organizing...")
        provider_display = {"ollama": "Ollama", "openai": "OpenAI", "anthropic": "Anthropic"}.get(provider_name, provider_name)
        self._show_message(f"Organizing feedback using {provider_display}...\nThis may take a moment.")

        def organize_thread():
            try:
                settings = self.settings_manager.load_settings()

                # Choose between organized and structured feedback
                if selected_mode == "structured":
                    # Use structured feedback conversion
                    result = self.feedback_organizer.organize_structured_feedback(
                        transcript=self.current_transcript,
                        rubric=self.current_rubric,
                        instruction_prompt=settings.feedback.instruction_prompt,
                        provider_name=provider_name
                    )
                else:
                    # Use traditional organized feedback
                    result = self.feedback_organizer.organize_feedback(
                        transcript=self.current_transcript,
                        rubric=self.current_rubric,
                        detail_level=settings.feedback.feedback_detail_level,
                        provider_name=provider_name
                    )

                if result:
                    # Include raw transcript if setting is enabled
                    if not settings.feedback.include_raw_transcript:
                        result.raw_transcript = ""

                    self.current_feedback = result
                    self.after(0, lambda: self._display_feedback(result))
                else:
                    error_msg = self._get_provider_error_message(provider_name)
                    self.after(0, lambda: self._show_error(error_msg))

            except Exception as e:
                error_msg = self._get_provider_error_message(provider_name, str(e))
                self.after(0, lambda: self._show_error(error_msg))
            finally:
                self.after(0, lambda: self.organize_btn.configure(state="normal", text="Organize"))

        threading.Thread(target=organize_thread, daemon=True).start()

    def _try_start_ollama(self):
        """Attempt to start Ollama if it's not running."""
        import subprocess
        import platform

        try:
            # Check if Ollama is available but not responding
            provider = self.feedback_organizer.get_provider("ollama")
            if provider and not provider.is_available():
                system = platform.system()

                # Try to start Ollama service
                if system == "Windows":
                    # On Windows, Ollama usually runs as a service or app
                    subprocess.Popen(["ollama", "serve"],
                                   creationflags=subprocess.CREATE_NO_WINDOW,
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
                elif system == "Darwin":  # macOS
                    subprocess.Popen(["ollama", "serve"],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
                elif system == "Linux":
                    subprocess.Popen(["ollama", "serve"],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)

                # Give it a moment to start
                import time
                time.sleep(2)
        except Exception:
            # Silently fail - we'll show a proper error message later if needed
            pass

    def _get_provider_error_message(self, provider_name: str, exception_msg: str = "") -> str:
        """Generate helpful error message based on provider."""
        # Parse common error patterns
        is_auth_error = any(phrase in exception_msg.lower() for phrase in
                           ["401", "invalid_api_key", "incorrect api key", "unauthorized", "authentication"])
        is_quota_error = any(phrase in exception_msg.lower() for phrase in
                            ["429", "quota", "rate limit", "insufficient_quota"])
        is_network_error = any(phrase in exception_msg.lower() for phrase in
                              ["connection", "timeout", "network", "unreachable"])
        is_policy_error = any(phrase in exception_msg.lower() for phrase in
                             ["404", "data policy", "no endpoints found", "privacy"])

        if provider_name == "ollama":
            return (
                "❌ Ollama Connection Failed\n\n"
                "Ollama is not running or not installed.\n\n"
                "To fix this:\n"
                "1. Download Ollama from: https://ollama.com/download\n"
                "2. Install and run Ollama\n"
                "3. Run: ollama pull llama2\n"
                "4. Make sure Ollama is running in the background\n\n"
                "Or switch to OpenAI/Anthropic in Settings."
            )

        elif provider_name == "openai":
            if is_auth_error:
                return (
                    "❌ Invalid OpenAI API Key\n\n"
                    "Your OpenAI API key is incorrect or missing.\n\n"
                    "To fix this:\n"
                    "1. Go to: https://platform.openai.com/api-keys\n"
                    "2. Create a new API key or copy your existing key\n"
                    "3. Click the ⚙ Settings button (top right)\n"
                    "4. Select 'LLM Provider' tab\n"
                    "5. Paste your API key in the OpenAI API Key field\n"
                    "6. Click Save\n\n"
                    "Note: Make sure you copy the complete key starting with 'sk-'"
                )
            elif is_quota_error:
                return (
                    "❌ OpenAI Quota Exceeded\n\n"
                    "You have exceeded your OpenAI usage quota or rate limit.\n\n"
                    "To fix this:\n"
                    "1. Check your usage at: https://platform.openai.com/usage\n"
                    "2. Add credits to your account if needed\n"
                    "3. Wait a few minutes if you hit the rate limit\n\n"
                    "Or switch to Ollama (free) or Anthropic in Settings."
                )
            elif is_network_error:
                return (
                    "❌ OpenAI Connection Error\n\n"
                    "Cannot connect to OpenAI servers.\n\n"
                    "To fix this:\n"
                    "1. Check your internet connection\n"
                    "2. Try again in a few moments\n"
                    "3. Check if OpenAI services are down: https://status.openai.com\n\n"
                    "Or switch to Ollama (local) in Settings."
                )
            else:
                return (
                    "❌ OpenAI Error\n\n"
                    "An error occurred with OpenAI API.\n\n"
                    f"Error details: {exception_msg}\n\n"
                    "To fix this:\n"
                    "1. Click ⚙ Settings and verify your OpenAI API key\n"
                    "2. Make sure you have credits in your account\n"
                    "3. Try switching to Ollama or Anthropic"
                )

        elif provider_name == "anthropic":
            if is_auth_error:
                return (
                    "❌ Invalid Anthropic API Key\n\n"
                    "Your Anthropic API key is incorrect or missing.\n\n"
                    "To fix this:\n"
                    "1. Go to: https://console.anthropic.com/settings/keys\n"
                    "2. Create a new API key or copy your existing key\n"
                    "3. Click the ⚙ Settings button (top right)\n"
                    "4. Select 'LLM Provider' tab\n"
                    "5. Paste your API key in the Anthropic API Key field\n"
                    "6. Click Save\n\n"
                    "Note: Make sure you copy the complete key starting with 'sk-ant-'"
                )
            elif is_quota_error:
                return (
                    "❌ Anthropic Quota Exceeded\n\n"
                    "You have exceeded your Anthropic usage quota or rate limit.\n\n"
                    "To fix this:\n"
                    "1. Check your usage at: https://console.anthropic.com\n"
                    "2. Add credits to your account if needed\n"
                    "3. Wait a few minutes if you hit the rate limit\n\n"
                    "Or switch to Ollama (free) or OpenAI in Settings."
                )
            elif is_network_error:
                return (
                    "❌ Anthropic Connection Error\n\n"
                    "Cannot connect to Anthropic servers.\n\n"
                    "To fix this:\n"
                    "1. Check your internet connection\n"
                    "2. Try again in a few moments\n"
                    "3. Check if Anthropic services are down\n\n"
                    "Or switch to Ollama (local) in Settings."
                )
            else:
                return (
                    "❌ Anthropic Error\n\n"
                    "An error occurred with Anthropic API.\n\n"
                    f"Error details: {exception_msg}\n\n"
                    "To fix this:\n"
                    "1. Click ⚙ Settings and verify your Anthropic API key\n"
                    "2. Make sure you have credits in your account\n"
                    "3. Try switching to Ollama or OpenAI"
                )

        elif provider_name == "openrouter":
            if is_policy_error:
                return (
                    "❌ OpenRouter Data Policy Configuration Required\n\n"
                    "Free models require specific privacy settings.\n\n"
                    "To fix this:\n"
                    "1. Go to: https://openrouter.ai/settings/privacy\n"
                    "2. Under 'Model Data Policies', enable:\n"
                    "   ✓ Allow free models\n"
                    "   ✓ Allow fallback to free models\n"
                    "3. Save your privacy settings\n"
                    "4. Return here and click 'Organize' again\n\n"
                    "Working free models:\n"
                    "• meta-llama/llama-3.1-8b-instruct:free\n"
                    "• google/gemma-2-9b-it:free\n"
                    "• qwen/qwen-2.5-7b-instruct:free\n\n"
                    "Note: Make sure your model name ends with ':free'"
                )
            elif is_auth_error:
                return (
                    "❌ Invalid OpenRouter API Key\n\n"
                    "Your OpenRouter API key is incorrect or missing.\n\n"
                    "To fix this:\n"
                    "1. Go to: https://openrouter.ai/keys\n"
                    "2. Create a new API key or copy your existing key\n"
                    "3. Click the ⚙ Settings button (top right)\n"
                    "4. Select 'LLM Provider' tab\n"
                    "5. Select 'OpenRouter' option\n"
                    "6. Paste your API key in the API Key field\n"
                    "7. Click Save\n\n"
                    "Note: OpenRouter offers free models like Llama 3.1!"
                )
            elif is_quota_error:
                return (
                    "❌ OpenRouter Quota Exceeded\n\n"
                    "You have exceeded your OpenRouter usage quota or rate limit.\n\n"
                    "To fix this:\n"
                    "1. Check your usage at: https://openrouter.ai/activity\n"
                    "2. Add credits to your account if using paid models\n"
                    "3. Switch to free models (e.g., meta-llama/llama-3.1-8b-instruct:free)\n"
                    "4. Wait a few minutes if you hit the rate limit\n\n"
                    "Or switch to Ollama (local, free) in Settings."
                )
            elif is_network_error:
                return (
                    "❌ OpenRouter Connection Error\n\n"
                    "Cannot connect to OpenRouter servers.\n\n"
                    "To fix this:\n"
                    "1. Check your internet connection\n"
                    "2. Try again in a few moments\n"
                    "3. Check if OpenRouter services are down\n\n"
                    "Or switch to Ollama (local) in Settings."
                )
            else:
                return (
                    "❌ OpenRouter Error\n\n"
                    "An error occurred with OpenRouter API.\n\n"
                    f"Error details: {exception_msg}\n\n"
                    "To fix this:\n"
                    "1. Click ⚙ Settings and verify your OpenRouter API key\n"
                    "2. Check that the model name is correct\n"
                    "3. See available models at: https://openrouter.ai/models\n"
                    "4. Try switching to a free model or Ollama"
                )

        else:
            return f"❌ Failed to organize feedback.\n\n{exception_msg}"

    def _display_feedback(self, feedback):
        """Display organized or structured feedback with copy buttons for each section."""
        # Clear existing feedback display
        for widget in self.feedback_scroll.winfo_children():
            widget.destroy()

        # Calculate and display word count
        word_count = self._calculate_word_count(feedback)
        self.word_count_label.configure(text=f"Word count: {word_count}")

        if isinstance(feedback, OrganizedFeedback):
            self._display_organized_feedback(feedback)
        elif isinstance(feedback, StructuredFeedback):
            self._display_structured_feedback(feedback)
        else:
            # Fallback for unknown feedback type
            label = ctk.CTkLabel(
                self.feedback_scroll,
                text=str(feedback),
                font=ctk.CTkFont(size=self.current_font_size),
                wraplength=900,
                justify="left"
            )
            label.pack(pady=10, padx=10, anchor="w")

        # Enable export buttons
        self.export_btn.configure(state="normal")
        self.export_dropdown.configure(state="normal")

    def _display_organized_feedback(self, feedback: OrganizedFeedback):
        """Display organized feedback with sections and copy buttons."""
        # Summary section
        if feedback.summary:
            self._create_feedback_section(
                "Summary",
                feedback.summary,
                is_first=True
            )

        # Criteria sections
        for criterion, text in feedback.criterion_feedback.items():
            self._create_feedback_section(criterion, text)

    def _display_structured_feedback(self, feedback: StructuredFeedback):
        """Display structured feedback with sections and copy buttons."""
        # Parse structured feedback into sections
        # Typically has: Overall Summary, Strengths, Areas for Improvement, Closing Comment
        lines = feedback.feedback_text.split('\n')

        current_section = None
        current_content = []
        sections = []

        for line in lines:
            # Detect section headers (lines that start with ## or ### or are all caps)
            if line.startswith('##') or line.startswith('###'):
                if current_section:
                    sections.append((current_section, '\n'.join(current_content)))
                # Clean markdown from section title
                current_section = line.replace('###', '').replace('##', '').strip()
                # Remove any remaining ** markers
                current_section = current_section.replace('**', '')
                current_content = []
            elif line.strip() and line.strip().isupper() and len(line.strip().split()) <= 5:
                # All caps line (likely a header)
                if current_section:
                    sections.append((current_section, '\n'.join(current_content)))
                current_section = line.strip()
                current_content = []
            else:
                if line.strip():
                    current_content.append(line)

        # Add last section
        if current_section:
            sections.append((current_section, '\n'.join(current_content)))

        # If no sections detected, treat as single block
        if not sections:
            self._create_feedback_section(
                "Feedback",
                feedback.feedback_text,
                is_first=True
            )
        else:
            # Display each section
            for i, (section_name, section_content) in enumerate(sections):
                self._create_feedback_section(
                    section_name,
                    section_content,
                    is_first=(i == 0)
                )

    def _create_feedback_section(self, title: str, content: str, is_first: bool = False):
        """Create a single feedback section with copy button."""
        # Clean markdown formatting from content for display
        clean_content = self._clean_markdown(content)

        # Section container
        section_frame = ctk.CTkFrame(
            self.feedback_scroll,
            fg_color=("white", "gray25"),
            corner_radius=8
        )
        section_frame.pack(fill="x", padx=10, pady=(10 if is_first else 5, 5))

        # Header with title and copy button
        header_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(size=self.current_font_size + 2, weight="bold"),
            anchor="w"
        )
        title_label.pack(side="left")

        copy_btn = ctk.CTkButton(
            header_frame,
            text="📋 Copy",
            command=lambda: self._copy_to_clipboard(clean_content),
            width=80,
            height=26,
            font=ctk.CTkFont(size=10)
        )
        copy_btn.pack(side="right")

        # Content text
        content_label = ctk.CTkLabel(
            section_frame,
            text=clean_content,
            font=ctk.CTkFont(size=self.current_font_size),
            wraplength=880,
            justify="left",
            anchor="w"
        )
        content_label.pack(fill="x", padx=10, pady=(0, 10), anchor="w")

    def _export_feedback(self, choice: str):
        """Export feedback in selected format."""
        if not self.current_feedback:
            messagebox.showwarning("Warning", "No feedback to export")
            return

        # Reset dropdown to "More..." after selection
        if choice != "Copy to Clipboard":
            self.export_var.set("More...")

        try:
            if choice == "Copy to Clipboard":
                if FeedbackExporter.to_clipboard(self.current_feedback, "plain"):
                    messagebox.showinfo("Success", "Feedback copied to clipboard!")
                else:
                    messagebox.showerror("Error", "Failed to copy to clipboard")

            elif choice == "Save as Text":
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
                )
                if file_path:
                    if FeedbackExporter.to_text_file(self.current_feedback, Path(file_path)):
                        messagebox.showinfo("Success", f"Saved to {Path(file_path).name}")
                    else:
                        messagebox.showerror("Error", "Failed to save file")

            elif choice == "Save as Markdown":
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".md",
                    filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
                )
                if file_path:
                    if FeedbackExporter.to_markdown_file(self.current_feedback, Path(file_path)):
                        messagebox.showinfo("Success", f"Saved to {Path(file_path).name}")
                    else:
                        messagebox.showerror("Error", "Failed to save file")

            elif choice == "Save as PDF":
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
                )
                if file_path:
                    if FeedbackExporter.to_pdf(self.current_feedback, Path(file_path)):
                        messagebox.showinfo("Success", f"Saved to {Path(file_path).name}")
                    else:
                        messagebox.showerror("Error", "Failed to save PDF")

            elif choice == "Save as Word":
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".docx",
                    filetypes=[("Word documents", "*.docx"), ("All files", "*.*")]
                )
                if file_path:
                    if FeedbackExporter.to_word(self.current_feedback, Path(file_path)):
                        messagebox.showinfo("Success", f"Saved to {Path(file_path).name}")
                    else:
                        messagebox.showerror("Error", "Failed to save Word document")

        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")

    def _show_message(self, message: str):
        """Show a message in the feedback display."""
        # Clear existing content
        for widget in self.feedback_scroll.winfo_children():
            widget.destroy()

        # Show message
        label = ctk.CTkLabel(
            self.feedback_scroll,
            text=message,
            font=ctk.CTkFont(size=self.current_font_size),
            text_color="gray",
            wraplength=800
        )
        label.pack(pady=50, padx=20)

    def _show_error(self, message: str):
        """Show error in feedback display."""
        # Clear existing content
        for widget in self.feedback_scroll.winfo_children():
            widget.destroy()

        # Show error
        label = ctk.CTkLabel(
            self.feedback_scroll,
            text=f"❌ Error:\n\n{message}",
            font=ctk.CTkFont(size=self.current_font_size),
            text_color="red",
            wraplength=800,
            justify="left"
        )
        label.pack(pady=50, padx=20)

    def clear(self):
        """Clear feedback panel."""
        self.current_feedback = None
        self.current_transcript = ""
        self._show_message("Select a rubric and transcribe audio to organize feedback.")
        self.word_count_label.configure(text="")
        self.export_btn.configure(state="disabled")
        self.export_dropdown.configure(state="disabled")
        self.transcript_toggle_btn.configure(state="disabled")
        # Hide transcript drawer if open
        if self.transcript_visible:
            self._toggle_transcript()
        self._update_organize_button()
