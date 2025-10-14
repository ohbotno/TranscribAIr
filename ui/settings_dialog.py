"""
Settings dialog for configuring LLM providers and feedback options.
"""
import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Callable

from core.settings import SettingsManager, AppSettings, LLMProvider


class SettingsDialog(ctk.CTkToplevel):
    """Dialog for application settings."""

    def __init__(self, parent, settings_manager: SettingsManager, on_save: Optional[Callable] = None):
        super().__init__(parent)

        self.settings_manager = settings_manager
        self.settings = settings_manager.load_settings()
        self.on_save_callback = on_save

        # Window setup
        self.title("Settings")
        self.geometry("650x700")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._create_ui()
        self._load_settings()

    def _create_ui(self):
        """Create settings UI."""
        # Button frame at bottom (pack first so it doesn't get pushed off-screen)
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        ctk.CTkButton(
            button_frame,
            text="Save",
            command=self._save_settings,
            width=120,
            fg_color="green"
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            width=120,
            fg_color="gray"
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Reset to Defaults",
            command=self._reset_defaults,
            width=140,
            fg_color="orange"
        ).pack(side="left", padx=5)

        # Main container with tabs (pack after buttons)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tabs
        self.tabview.add("LLM Provider")
        self.tabview.add("Feedback")

        # LLM Provider tab
        self._create_llm_tab()

        # Feedback tab
        self._create_feedback_tab()

    def _create_llm_tab(self):
        """Create LLM provider settings tab."""
        tab = self.tabview.tab("LLM Provider")

        # Provider selection
        provider_frame = ctk.CTkFrame(tab)
        provider_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            provider_frame,
            text="LLM Provider:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self.provider_var = ctk.StringVar(value=LLMProvider.OLLAMA.value)
        providers = [
            ("Ollama (Local)", LLMProvider.OLLAMA.value),
            ("OpenAI", LLMProvider.OPENAI.value),
            ("Anthropic Claude", LLMProvider.ANTHROPIC.value),
            ("OpenRouter", LLMProvider.OPENROUTER.value)
        ]

        for label, value in providers:
            rb = ctk.CTkRadioButton(
                provider_frame,
                text=label,
                variable=self.provider_var,
                value=value,
                command=self._update_provider_panels
            )
            rb.pack(anchor="w", padx=20, pady=5)

        # Scrollable frame for provider settings
        settings_scroll = ctk.CTkScrollableFrame(tab, height=400)
        settings_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Ollama settings
        self.ollama_frame = ctk.CTkFrame(settings_scroll)
        self._create_ollama_settings(self.ollama_frame)

        # OpenAI settings
        self.openai_frame = ctk.CTkFrame(settings_scroll)
        self._create_openai_settings(self.openai_frame)

        # Anthropic settings
        self.anthropic_frame = ctk.CTkFrame(settings_scroll)
        self._create_anthropic_settings(self.anthropic_frame)

        # OpenRouter settings
        self.openrouter_frame = ctk.CTkFrame(settings_scroll)
        self._create_openrouter_settings(self.openrouter_frame)

    def _create_ollama_settings(self, parent):
        """Create Ollama settings section."""
        ctk.CTkLabel(
            parent,
            text="Ollama Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # Model
        model_frame = ctk.CTkFrame(parent)
        model_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(model_frame, text="Model:", width=120).pack(side="left", padx=5)
        self.ollama_model_entry = ctk.CTkEntry(model_frame, width=300)
        self.ollama_model_entry.pack(side="left", padx=5)

        ctk.CTkLabel(
            parent,
            text="(e.g., llama2, mistral, codellama)",
            text_color="gray",
            font=ctk.CTkFont(size=10)
        ).pack(anchor="w", padx=140)

        # Base URL
        url_frame = ctk.CTkFrame(parent)
        url_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(url_frame, text="Base URL:", width=120).pack(side="left", padx=5)
        self.ollama_url_entry = ctk.CTkEntry(url_frame, width=300)
        self.ollama_url_entry.pack(side="left", padx=5)

        # Help text
        help_text = ctk.CTkTextbox(parent, height=80, fg_color="transparent")
        help_text.pack(fill="x", padx=10, pady=10)
        help_text.insert("1.0",
            "Ollama runs locally on your machine. Install from ollama.ai.\n"
            "This is the recommended option for privacy and no API costs.\n"
            "Make sure Ollama is running before using this option."
        )
        help_text.configure(state="disabled")

    def _create_openai_settings(self, parent):
        """Create OpenAI settings section."""
        ctk.CTkLabel(
            parent,
            text="OpenAI Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # API Key
        key_frame = ctk.CTkFrame(parent)
        key_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(key_frame, text="API Key:", width=120).pack(side="left", padx=5)
        self.openai_key_entry = ctk.CTkEntry(key_frame, width=300, show="*")
        self.openai_key_entry.pack(side="left", padx=5)

        # Model
        model_frame = ctk.CTkFrame(parent)
        model_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(model_frame, text="Model:", width=120).pack(side="left", padx=5)
        self.openai_model_var = ctk.StringVar(value="gpt-3.5-turbo")
        openai_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]
        self.openai_model_dropdown = ctk.CTkOptionMenu(
            model_frame,
            variable=self.openai_model_var,
            values=openai_models,
            width=300
        )
        self.openai_model_dropdown.pack(side="left", padx=5)

        # Help text
        help_text = ctk.CTkTextbox(parent, height=60, fg_color="transparent")
        help_text.pack(fill="x", padx=10, pady=10)
        help_text.insert("1.0",
            "Get your API key from platform.openai.com/api-keys.\n"
            "Usage is billed per token. GPT-3.5-turbo is cheaper, GPT-4 is more capable."
        )
        help_text.configure(state="disabled")

    def _create_anthropic_settings(self, parent):
        """Create Anthropic settings section."""
        ctk.CTkLabel(
            parent,
            text="Anthropic Claude Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # API Key
        key_frame = ctk.CTkFrame(parent)
        key_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(key_frame, text="API Key:", width=120).pack(side="left", padx=5)
        self.anthropic_key_entry = ctk.CTkEntry(key_frame, width=300, show="*")
        self.anthropic_key_entry.pack(side="left", padx=5)

        # Model
        model_frame = ctk.CTkFrame(parent)
        model_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(model_frame, text="Model:", width=120).pack(side="left", padx=5)
        self.anthropic_model_var = ctk.StringVar(value="claude-3-haiku-20240307")
        anthropic_models = [
            "claude-3-haiku-20240307",
            "claude-3-sonnet-20240229",
            "claude-3-opus-20240229"
        ]
        self.anthropic_model_dropdown = ctk.CTkOptionMenu(
            model_frame,
            variable=self.anthropic_model_var,
            values=anthropic_models,
            width=300
        )
        self.anthropic_model_dropdown.pack(side="left", padx=5)

        # Help text
        help_text = ctk.CTkTextbox(parent, height=60, fg_color="transparent")
        help_text.pack(fill="x", padx=10, pady=10)
        help_text.insert("1.0",
            "Get your API key from console.anthropic.com.\n"
            "Haiku is fastest/cheapest, Sonnet is balanced, Opus is most capable."
        )
        help_text.configure(state="disabled")

    def _create_openrouter_settings(self, parent):
        """Create OpenRouter settings section."""
        ctk.CTkLabel(
            parent,
            text="OpenRouter Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # API Key
        key_frame = ctk.CTkFrame(parent)
        key_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(key_frame, text="API Key:", width=120).pack(side="left", padx=5)
        self.openrouter_key_entry = ctk.CTkEntry(key_frame, width=300, show="*")
        self.openrouter_key_entry.pack(side="left", padx=5)

        # Model
        model_frame = ctk.CTkFrame(parent)
        model_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(model_frame, text="Model:", width=120).pack(side="left", padx=5)
        self.openrouter_model_entry = ctk.CTkEntry(model_frame, width=300)
        self.openrouter_model_entry.pack(side="left", padx=5)

        ctk.CTkLabel(
            parent,
            text="Free models: qwen/qwen-2.5-7b-instruct:free, meta-llama/llama-3.1-8b-instruct:free",
            text_color="gray",
            font=ctk.CTkFont(size=10)
        ).pack(anchor="w", padx=140)

        # Help text
        help_text = ctk.CTkTextbox(parent, height=100, fg_color="transparent")
        help_text.pack(fill="x", padx=10, pady=10)
        help_text.insert("1.0",
            "OpenRouter provides access to multiple AI models through one API.\n"
            "Get your API key from openrouter.ai/keys.\n\n"
            "IMPORTANT for free models: Go to openrouter.ai/settings/privacy\n"
            "and enable 'Allow free models' under Model Data Policies.\n\n"
            "See all models at: openrouter.ai/models"
        )
        help_text.configure(state="disabled")

    def _create_feedback_tab(self):
        """Create feedback settings tab."""
        tab = self.tabview.tab("Feedback")

        container = ctk.CTkFrame(tab)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Auto-organize toggle
        auto_frame = ctk.CTkFrame(container)
        auto_frame.pack(fill="x", padx=10, pady=10)

        self.auto_organize_var = ctk.BooleanVar(value=False)
        self.auto_organize_check = ctk.CTkCheckBox(
            auto_frame,
            text="Automatically organize feedback after transcription",
            variable=self.auto_organize_var
        )
        self.auto_organize_check.pack(anchor="w", padx=10, pady=10)

        # Detail level
        detail_frame = ctk.CTkFrame(container)
        detail_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            detail_frame,
            text="Feedback Detail Level:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self.detail_var = ctk.StringVar(value="detailed")
        ctk.CTkRadioButton(
            detail_frame,
            text="Brief (concise, actionable feedback)",
            variable=self.detail_var,
            value="brief"
        ).pack(anchor="w", padx=20, pady=5)

        ctk.CTkRadioButton(
            detail_frame,
            text="Detailed (comprehensive feedback with examples)",
            variable=self.detail_var,
            value="detailed"
        ).pack(anchor="w", padx=20, pady=5)

        # Include raw transcript
        raw_frame = ctk.CTkFrame(container)
        raw_frame.pack(fill="x", padx=10, pady=10)

        self.include_raw_var = ctk.BooleanVar(value=True)
        self.include_raw_check = ctk.CTkCheckBox(
            raw_frame,
            text="Include raw transcript in organized feedback",
            variable=self.include_raw_var
        )
        self.include_raw_check.pack(anchor="w", padx=10, pady=10)

    def _update_provider_panels(self):
        """Update which provider settings panel is visible."""
        # Hide all
        self.ollama_frame.pack_forget()
        self.openai_frame.pack_forget()
        self.anthropic_frame.pack_forget()
        self.openrouter_frame.pack_forget()

        # Show selected
        provider = self.provider_var.get()
        if provider == LLMProvider.OLLAMA.value:
            self.ollama_frame.pack(fill="both", expand=True, pady=10)
        elif provider == LLMProvider.OPENAI.value:
            self.openai_frame.pack(fill="both", expand=True, pady=10)
        elif provider == LLMProvider.ANTHROPIC.value:
            self.anthropic_frame.pack(fill="both", expand=True, pady=10)
        elif provider == LLMProvider.OPENROUTER.value:
            self.openrouter_frame.pack(fill="both", expand=True, pady=10)

    def _load_settings(self):
        """Load current settings into form."""
        # LLM settings
        self.provider_var.set(self.settings.llm.provider)
        self.ollama_model_entry.insert(0, self.settings.llm.ollama_model)
        self.ollama_url_entry.insert(0, self.settings.llm.ollama_base_url)
        self.openai_key_entry.insert(0, self.settings.llm.openai_api_key)
        self.openai_model_var.set(self.settings.llm.openai_model)
        self.anthropic_key_entry.insert(0, self.settings.llm.anthropic_api_key)
        self.anthropic_model_var.set(self.settings.llm.anthropic_model)
        self.openrouter_key_entry.insert(0, self.settings.llm.openrouter_api_key)
        self.openrouter_model_entry.insert(0, self.settings.llm.openrouter_model)

        # Feedback settings
        self.auto_organize_var.set(self.settings.feedback.auto_organize)
        self.detail_var.set(self.settings.feedback.feedback_detail_level)
        self.include_raw_var.set(self.settings.feedback.include_raw_transcript)

        # Update UI
        self._update_provider_panels()

    def _save_settings(self):
        """Save settings."""
        # Update LLM settings
        self.settings.llm.provider = self.provider_var.get()
        self.settings.llm.ollama_model = self.ollama_model_entry.get()
        self.settings.llm.ollama_base_url = self.ollama_url_entry.get()
        self.settings.llm.openai_api_key = self.openai_key_entry.get()
        self.settings.llm.openai_model = self.openai_model_var.get()
        self.settings.llm.anthropic_api_key = self.anthropic_key_entry.get()
        self.settings.llm.anthropic_model = self.anthropic_model_var.get()
        self.settings.llm.openrouter_api_key = self.openrouter_key_entry.get()
        self.settings.llm.openrouter_model = self.openrouter_model_entry.get()

        # Update feedback settings
        self.settings.feedback.auto_organize = self.auto_organize_var.get()
        self.settings.feedback.feedback_detail_level = self.detail_var.get()
        self.settings.feedback.include_raw_transcript = self.include_raw_var.get()

        # Save to disk
        if self.settings_manager.save_settings(self.settings):
            messagebox.showinfo("Success", "Settings saved successfully")
            if self.on_save_callback:
                self.on_save_callback(self.settings)
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to save settings")

    def _reset_defaults(self):
        """Reset settings to defaults."""
        if messagebox.askyesno("Confirm", "Reset all settings to defaults?"):
            self.settings = self.settings_manager.reset_to_defaults()

            # Clear and reload form
            self.ollama_model_entry.delete(0, "end")
            self.ollama_url_entry.delete(0, "end")
            self.openai_key_entry.delete(0, "end")
            self.anthropic_key_entry.delete(0, "end")
            self.openrouter_key_entry.delete(0, "end")
            self.openrouter_model_entry.delete(0, "end")

            self._load_settings()
            messagebox.showinfo("Success", "Settings reset to defaults")
