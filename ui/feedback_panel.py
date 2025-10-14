"""
Feedback panel component for displaying organized feedback.
Reusable component for both Record and Upload tabs.
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Optional, Callable
from pathlib import Path
import threading

from core.feedback import OrganizedFeedback, FeedbackOrganizer
from core.export import FeedbackExporter
from core.rubric import Rubric, RubricManager
from core.settings import SettingsManager
from ui.rubric_dialog import RubricSelectorDialog


class FeedbackPanel(ctk.CTkFrame):
    """Panel for displaying and managing organized feedback."""

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

    def _create_ui(self):
        """Create feedback panel UI."""
        # Header with simplified controls
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=5, pady=5)

        # Rubric info label (left side)
        self.rubric_label = ctk.CTkLabel(
            header,
            text="No rubric selected",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.rubric_label.pack(side="left", padx=10)

        # Control buttons (right side)
        button_container = ctk.CTkFrame(header)
        button_container.pack(side="right", padx=10)

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

        # Feedback display (scrollable) - takes most space
        self.feedback_text = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(size=12),
            wrap="word"
        )
        self.feedback_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.feedback_text.insert("1.0", "Select a rubric and transcribe audio to organize feedback.")
        self.feedback_text.configure(state="disabled")

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
        """Initialize provider with settings default."""
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

    def _on_provider_changed(self, choice: str):
        """Handle provider selection change."""
        provider_map = {
            "Ollama": "ollama",
            "OpenAI": "openai",
            "Anthropic": "anthropic",
            "OpenRouter": "openrouter"
        }
        self.selected_provider = provider_map.get(choice, "ollama")

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

        # Auto-organize if transcript exists and auto-organize is enabled
        settings = self.settings_manager.load_settings()
        if settings.feedback.auto_organize and self.current_transcript:
            self._organize_feedback()

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

        # Disable button and show progress
        self.organize_btn.configure(state="disabled", text="Organizing...")
        self.feedback_text.configure(state="normal")
        self.feedback_text.delete("1.0", "end")
        provider_display = {"ollama": "Ollama", "openai": "OpenAI", "anthropic": "Anthropic"}.get(provider_name, provider_name)
        self.feedback_text.insert("1.0", f"Organizing feedback using {provider_display}...\nThis may take a moment.")
        self.feedback_text.configure(state="disabled")

        def organize_thread():
            try:
                settings = self.settings_manager.load_settings()

                # Organize feedback with selected provider
                organized = self.feedback_organizer.organize_feedback(
                    transcript=self.current_transcript,
                    rubric=self.current_rubric,
                    detail_level=settings.feedback.feedback_detail_level,
                    provider_name=provider_name
                )

                if organized:
                    # Include raw transcript if setting is enabled
                    if not settings.feedback.include_raw_transcript:
                        organized.raw_transcript = ""

                    self.current_feedback = organized
                    self.after(0, lambda: self._display_feedback(organized))
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

    def _display_feedback(self, feedback: OrganizedFeedback):
        """Display organized feedback."""
        self.feedback_text.configure(state="normal")
        self.feedback_text.delete("1.0", "end")
        self.feedback_text.insert("1.0", feedback.to_markdown())
        self.feedback_text.configure(state="disabled")

        # Enable export buttons
        self.export_btn.configure(state="normal")
        self.export_dropdown.configure(state="normal")

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

    def _show_error(self, message: str):
        """Show error in feedback display."""
        self.feedback_text.configure(state="normal")
        self.feedback_text.delete("1.0", "end")
        self.feedback_text.insert("1.0", f"❌ Error:\n\n{message}")
        self.feedback_text.configure(state="disabled")

    def clear(self):
        """Clear feedback panel."""
        self.current_feedback = None
        self.current_transcript = ""
        self.feedback_text.configure(state="normal")
        self.feedback_text.delete("1.0", "end")
        self.feedback_text.insert("1.0", "Select a rubric and transcribe audio to organize feedback.")
        self.feedback_text.configure(state="disabled")
        self.export_btn.configure(state="disabled")
        self.export_dropdown.configure(state="disabled")
        self.transcript_toggle_btn.configure(state="disabled")
        # Hide transcript drawer if open
        if self.transcript_visible:
            self._toggle_transcript()
        self._update_organize_button()
