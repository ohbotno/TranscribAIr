"""
Main application window for TranscribAIr.
Built with CustomTkinter for modern desktop UI.
"""
import customtkinter as ctk
from typing import Optional
from pathlib import Path
import threading
import urllib.request
import json
from tkinter import messagebox

from core import Transcriber
from core.rubric import RubricManager
from core.settings import SettingsManager
from core.feedback import FeedbackOrganizer
from .upload_tab import UploadTab
from .record_tab import RecordTab
from .settings_dialog import SettingsDialog

# Import version info
try:
    from __version__ import __version__, APP_NAME, APP_URL
except ImportError:
    __version__ = "1.0.0"
    APP_NAME = "TranscribAIr"
    APP_URL = "https://github.com/yourusername/TranscribAIr"


class MainWindow(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title(f"{APP_NAME} v{__version__}")
        self.geometry("1200x800")

        # Set theme
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # Initialize core systems
        self.transcriber = Transcriber()
        self.rubric_manager = RubricManager()
        self.settings_manager = SettingsManager()
        settings = self.settings_manager.load_settings()
        self.feedback_organizer = FeedbackOrganizer(settings.llm)

        self.current_transcript = ""

        # Create UI
        self._create_header()
        self._create_tabs()
        self._create_status_bar()

        # Track if model is loaded
        self.model_loaded = False

        # Bind keyboard shortcuts
        self._bind_keyboard_shortcuts()

    def _create_header(self):
        """Create header with model selector and settings."""
        header_frame = ctk.CTkFrame(self, corner_radius=10)
        header_frame.pack(fill="x", padx=10, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="TranscribAIr",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=15, pady=10)

        # Model selection frame
        model_frame = ctk.CTkFrame(header_frame)
        model_frame.pack(side="right", padx=15, pady=10)

        model_label = ctk.CTkLabel(
            model_frame,
            text="Model:",
            font=ctk.CTkFont(size=12)
        )
        model_label.pack(side="left", padx=(0, 10))

        # Model dropdown
        model_options = []
        for size, disk_size in self.transcriber.get_available_models().items():
            model_options.append(f"{size} ({disk_size})")

        self.model_var = ctk.StringVar(value=model_options[1])  # Default to "base"
        self.model_dropdown = ctk.CTkOptionMenu(
            model_frame,
            variable=self.model_var,
            values=model_options,
            command=self._on_model_changed,
            width=200
        )
        self.model_dropdown.pack(side="left", padx=(0, 10))

        # Load model button
        self.load_model_btn = ctk.CTkButton(
            model_frame,
            text="Load Model",
            command=self._load_model,
            width=120
        )
        self.load_model_btn.pack(side="left")

        # Timestamps checkbox
        self.timestamps_var = ctk.BooleanVar(value=False)
        self.timestamps_check = ctk.CTkCheckBox(
            model_frame,
            text="Include Timestamps",
            variable=self.timestamps_var
        )
        self.timestamps_check.pack(side="left", padx=(15, 0))

        # Settings button
        settings_btn = ctk.CTkButton(
            model_frame,
            text="⚙ Settings",
            command=self._open_settings,
            width=100
        )
        settings_btn.pack(side="left", padx=(15, 0))

        # About button
        about_btn = ctk.CTkButton(
            model_frame,
            text="ℹ About",
            command=self._show_about,
            width=80
        )
        about_btn.pack(side="left", padx=(10, 0))

    def _create_tabs(self):
        """Create tabbed interface for Upload and Record."""
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Create tabs
        self.tabview.add("Record Audio")
        self.tabview.add("Upload File")

        # Initialize tab contents with feedback support
        self.upload_tab = UploadTab(
            self.tabview.tab("Upload File"),
            on_transcribe=self._transcribe_file,
            rubric_manager=self.rubric_manager,
            settings_manager=self.settings_manager,
            feedback_organizer=self.feedback_organizer
        )

        self.record_tab = RecordTab(
            self.tabview.tab("Record Audio"),
            on_transcribe=self._transcribe_recording,
            rubric_manager=self.rubric_manager,
            settings_manager=self.settings_manager,
            feedback_organizer=self.feedback_organizer
        )

    def _create_status_bar(self):
        """Create status bar at bottom."""
        self.status_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.status_frame.pack(fill="x", side="bottom")

        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready - Please load a model to begin",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(side="left", padx=10, pady=5)

        # Progress bar (hidden by default)
        self.progress_bar = ctk.CTkProgressBar(self.status_frame, width=200)
        self.progress_bar.pack(side="right", padx=10, pady=5)
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()

    def _on_model_changed(self, choice: str):
        """Handle model selection change."""
        self.model_loaded = False
        self.load_model_btn.configure(text="Load Model")
        self._update_status("Model changed - click 'Load Model' to load")

    def _load_model(self):
        """Load selected Whisper model."""
        # Extract model size from selection (e.g., "base (~140 MB)" -> "base")
        model_size = self.model_var.get().split()[0]

        self._update_status(f"Loading model '{model_size}'...")
        self.load_model_btn.configure(state="disabled", text="Loading...")
        self.progress_bar.pack(side="right", padx=10, pady=5)
        self.progress_bar.set(0)
        self.progress_bar.start()

        def load_thread():
            try:
                self.transcriber.load_model(
                    model_size,
                    progress_callback=self._update_status
                )
                self.model_loaded = True
                self.after(0, lambda: self.load_model_btn.configure(
                    state="normal",
                    text="✓ Loaded",
                    fg_color="green"
                ))
                self.after(0, lambda: self._update_status(f"Model '{model_size}' ready"))
            except Exception as e:
                self.after(0, lambda: self._update_status(f"Error: {str(e)}"))
                self.after(0, lambda: self.load_model_btn.configure(
                    state="normal",
                    text="Load Model"
                ))
            finally:
                self.after(0, self.progress_bar.stop)
                self.after(0, self.progress_bar.pack_forget)

        threading.Thread(target=load_thread, daemon=True).start()

    def _transcribe_file(self, file_path: str):
        """Transcribe uploaded file."""
        if not self.model_loaded:
            self._update_status("Please load a model first")
            return

        self._update_status("Transcribing...")
        self.progress_bar.pack(side="right", padx=10, pady=5)
        self.progress_bar.start()

        def transcribe_thread():
            try:
                transcript = self.transcriber.transcribe(
                    file_path,
                    include_timestamps=self.timestamps_var.get(),
                    progress_callback=self._update_status
                )
                self.current_transcript = transcript
                self.after(0, lambda: self._display_transcript(transcript))
                # Update Upload tab with transcript
                self.after(0, lambda: self.upload_tab.set_transcript(transcript))
            except Exception as e:
                self.after(0, lambda: self._update_status(f"Error: {str(e)}"))
            finally:
                self.after(0, self.progress_bar.stop)
                self.after(0, self.progress_bar.pack_forget)

        threading.Thread(target=transcribe_thread, daemon=True).start()

    def _transcribe_recording(self, file_path: str):
        """Transcribe recorded audio."""
        if not self.model_loaded:
            self._update_status("Please load a model first")
            return

        self._update_status("Transcribing...")
        self.progress_bar.pack(side="right", padx=10, pady=5)
        self.progress_bar.start()

        def transcribe_thread():
            try:
                transcript = self.transcriber.transcribe(
                    file_path,
                    include_timestamps=self.timestamps_var.get(),
                    progress_callback=self._update_status
                )
                self.current_transcript = transcript
                self.after(0, lambda: self._display_transcript(transcript))
                # Update Record tab with transcript
                self.after(0, lambda: self.record_tab.set_transcript(transcript))
            except Exception as e:
                self.after(0, lambda: self._update_status(f"Error: {str(e)}"))
            finally:
                self.after(0, self.progress_bar.stop)
                self.after(0, self.progress_bar.pack_forget)

        threading.Thread(target=transcribe_thread, daemon=True).start()

    def _display_transcript(self, transcript: str):
        """Display transcript - now handled by tabs."""
        self._update_status("Transcription complete!")

    def _bind_keyboard_shortcuts(self):
        """Bind keyboard shortcuts for quick actions."""
        # Ctrl+R - Start/Stop recording (only on Record tab)
        self.bind("<Control-r>", self._shortcut_record)

        # Ctrl+E - Export feedback (copy to clipboard)
        self.bind("<Control-e>", self._shortcut_export)

        # Ctrl+N - New recording
        self.bind("<Control-n>", self._shortcut_new)

        # Ctrl+T - Transcribe
        self.bind("<Control-t>", self._shortcut_transcribe)

    def _shortcut_record(self, event=None):
        """Keyboard shortcut for record toggle."""
        if self.tabview.get() == "Record Audio":
            self.record_tab._toggle_recording()
        return "break"

    def _shortcut_export(self, event=None):
        """Keyboard shortcut for export (copy to clipboard)."""
        current_tab = self.tabview.get()
        if current_tab == "Upload File":
            panel = self.upload_tab.feedback_panel
        else:
            panel = self.record_tab.feedback_panel

        if panel.current_feedback and panel.export_btn.cget("state") == "normal":
            panel._export_feedback("Copy to Clipboard")
        return "break"

    def _shortcut_new(self, event=None):
        """Keyboard shortcut for new recording."""
        if self.tabview.get() == "Record Audio":
            if self.record_tab.new_btn.cget("state") == "normal":
                self.record_tab._new_recording()
        return "break"

    def _shortcut_transcribe(self, event=None):
        """Keyboard shortcut for transcribe."""
        current_tab = self.tabview.get()
        if current_tab == "Upload File":
            if self.upload_tab.transcribe_btn.cget("state") == "normal":
                self.upload_tab._transcribe()
        elif current_tab == "Record Audio":
            if self.record_tab.transcribe_btn.cget("state") == "normal":
                self.record_tab._transcribe()
        return "break"

    def _update_status(self, message: str):
        """Update status bar message."""
        self.status_label.configure(text=message)
        self.update_idletasks()

    def _open_settings(self):
        """Open settings dialog."""
        dialog = SettingsDialog(
            self,
            self.settings_manager,
            on_save=self._on_settings_saved
        )

    def _on_settings_saved(self, settings):
        """Handle settings save."""
        # Reload feedback organizer with new settings
        self.feedback_organizer = FeedbackOrganizer(settings.llm)

        # Update tabs with new organizer
        self.upload_tab.feedback_organizer = self.feedback_organizer
        self.record_tab.feedback_organizer = self.feedback_organizer

        # Update feedback panels in tabs
        if hasattr(self.upload_tab, 'feedback_panel'):
            self.upload_tab.feedback_panel.feedback_organizer = self.feedback_organizer
        if hasattr(self.record_tab, 'feedback_panel'):
            self.record_tab.feedback_panel.feedback_organizer = self.feedback_organizer

        self._update_status("Settings saved")

    def _check_for_updates(self):
        """Check for updates from GitHub releases."""
        try:
            # GitHub API endpoint for latest release
            api_url = f"{APP_URL.replace('github.com', 'api.github.com/repos')}/releases/latest"

            with urllib.request.urlopen(api_url, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get("tag_name", "").lstrip("v")
                download_url = data.get("html_url", APP_URL)

                # Compare versions (simple string comparison for semantic versioning)
                if latest_version and latest_version > __version__:
                    return True, latest_version, download_url
                else:
                    return False, __version__, None
        except Exception:
            # Silently fail on network errors
            return False, __version__, None

    def _show_about(self):
        """Show About dialog with version info and update check."""
        # Check for updates in background
        update_available = False
        latest_version = __version__
        download_url = None

        def check_updates():
            nonlocal update_available, latest_version, download_url
            update_available, latest_version, download_url = self._check_for_updates()

        # Run update check in background thread
        check_thread = threading.Thread(target=check_updates, daemon=True)
        check_thread.start()
        check_thread.join(timeout=3)  # Wait max 3 seconds

        # Build about message
        about_text = f"""{APP_NAME}
Version: {__version__}

AI-powered audio transcription and feedback organization tool.

Built with:
• Faster-Whisper for transcription
• CustomTkinter for modern UI
• Multiple LLM provider support

"""

        if update_available:
            about_text += f"🎉 New version available: v{latest_version}\n\n"
            update_text = f"A new version (v{latest_version}) is available!\n\nWould you like to download it?"
        else:
            about_text += "✓ You're using the latest version\n\n"
            update_text = None

        about_text += f"© 2025 Swansea University\n\nMIT License\n\n{APP_URL}"

        # Show about dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"About {APP_NAME}")
        dialog.geometry("500x400")
        dialog.resizable(False, False)

        # Make dialog modal
        dialog.transient(self)
        dialog.grab_set()

        # Center dialog on parent window
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 500) // 2
        y = self.winfo_y() + (self.winfo_height() - 400) // 2
        dialog.geometry(f"+{x}+{y}")

        # About text
        text_widget = ctk.CTkTextbox(
            dialog,
            width=460,
            height=300,
            font=ctk.CTkFont(size=12),
            wrap="word"
        )
        text_widget.pack(padx=20, pady=20)
        text_widget.insert("1.0", about_text)
        text_widget.configure(state="disabled")

        # Buttons frame
        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Download button (if update available)
        if update_available and download_url:
            def open_download():
                import webbrowser
                webbrowser.open(download_url)
                dialog.destroy()

            download_btn = ctk.CTkButton(
                btn_frame,
                text="Download Update",
                command=open_download,
                fg_color="green",
                width=150
            )
            download_btn.pack(side="left", padx=(0, 10))

        # Close button
        close_btn = ctk.CTkButton(
            btn_frame,
            text="Close",
            command=dialog.destroy,
            width=100
        )
        close_btn.pack(side="right")
