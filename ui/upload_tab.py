"""
Upload tab for file-based transcription with feedback support.
Handles file browsing and displays transcript/feedback side-by-side.
"""
import customtkinter as ctk
from typing import Callable, Optional
from pathlib import Path
import os

from core import AudioUtils
from core.rubric import RubricManager
from core.settings import SettingsManager
from core.feedback import FeedbackOrganizer
from .feedback_panel import FeedbackPanel


class UploadTab(ctk.CTkFrame):
    """Upload tab UI component with side-by-side transcript/feedback layout."""

    def __init__(
        self,
        parent,
        on_transcribe: Callable[[str], None],
        rubric_manager: RubricManager,
        settings_manager: SettingsManager,
        feedback_organizer: FeedbackOrganizer
    ):
        super().__init__(parent)
        self.on_transcribe_callback = on_transcribe
        self.rubric_manager = rubric_manager
        self.settings_manager = settings_manager
        self.feedback_organizer = feedback_organizer

        self.selected_file: Optional[str] = None
        self.audio_utils = AudioUtils()
        self.current_transcript = ""

        self._create_ui()

        # Pack the tab frame into its parent
        self.pack(fill="both", expand=True)

    def _create_ui(self):
        """Create upload tab UI with full-width feedback."""
        # Main container
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Top section - file selection
        upload_section = ctk.CTkFrame(main_container, height=250)
        upload_section.pack(fill="x", pady=(0, 10))
        upload_section.pack_propagate(False)

        self._create_upload_controls(upload_section)

        # Full-width feedback panel
        self.feedback_panel = FeedbackPanel(
            main_container,
            self.rubric_manager,
            self.settings_manager,
            self.feedback_organizer
        )
        self.feedback_panel.pack(fill="both", expand=True)

    def _create_upload_controls(self, parent):
        """Create file upload controls."""
        # File selection area (left side)
        drop_section = ctk.CTkFrame(parent)
        drop_section.pack(side="left", fill="both", expand=True, padx=(10, 5))

        # Drop zone
        self.drop_zone = ctk.CTkFrame(
            drop_section,
            corner_radius=10,
            border_width=2,
            border_color="gray"
        )
        self.drop_zone.pack(fill="both", expand=True, padx=10, pady=10)

        # Drop zone content
        drop_content = ctk.CTkFrame(self.drop_zone)
        drop_content.place(relx=0.5, rely=0.5, anchor="center")

        icon_label = ctk.CTkLabel(
            drop_content,
            text="📁",
            font=ctk.CTkFont(size=42)
        )
        icon_label.pack(pady=(0, 8))

        instruction_label = ctk.CTkLabel(
            drop_content,
            text="Drag and drop an audio file here\nor click 'Browse' below",
            font=ctk.CTkFont(size=13)
        )
        instruction_label.pack()

        supported_label = ctk.CTkLabel(
            drop_content,
            text="Supported: MP3, WAV, M4A, FLAC, OGG",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        supported_label.pack(pady=(8, 0))

        # Control panel (right side)
        control_section = ctk.CTkFrame(parent)
        control_section.pack(side="right", fill="both", expand=True, padx=(5, 10))

        # File info (hidden by default)
        self.info_frame = ctk.CTkFrame(control_section)
        self.info_frame.pack(fill="x", padx=10, pady=10)
        self.info_frame.pack_forget()

        info_header = ctk.CTkLabel(
            self.info_frame,
            text="Selected File",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        info_header.pack(pady=(5, 3), anchor="w")

        self.file_name_label = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.file_name_label.pack(pady=2, anchor="w")

        self.file_info_label = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.file_info_label.pack(pady=2, anchor="w")

        # Buttons
        button_section = ctk.CTkFrame(control_section)
        button_section.pack(fill="both", expand=True, padx=10, pady=10)

        browse_btn = ctk.CTkButton(
            button_section,
            text="Browse Files",
            command=self._browse_file,
            width=280,
            height=40
        )
        browse_btn.pack(pady=5)

        self.transcribe_btn = ctk.CTkButton(
            button_section,
            text="Transcribe",
            command=self._transcribe,
            width=280,
            height=36,
            state="disabled"
        )
        self.transcribe_btn.pack(pady=5)

        self.clear_btn = ctk.CTkButton(
            button_section,
            text="Clear",
            command=self._clear_file,
            width=280,
            height=36,
            fg_color="gray",
            state="disabled"
        )
        self.clear_btn.pack(pady=5)

        # Set up drag and drop
        self._setup_drag_drop()

    def _setup_drag_drop(self):
        """Set up drag and drop functionality."""
        # Note: tkinterdnd2 needs to be set up on the root window
        # This is a simplified version - full implementation would require
        # TkinterDnD.Tk() as root window instead of ctk.CTk()
        # For now, we'll rely on the browse button
        pass

    def _browse_file(self):
        """Open file browser dialog."""
        file_path = ctk.filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.m4a *.flac *.ogg *.aac *.wma *.opus"),
                ("All Files", "*.*")
            ]
        )

        if file_path:
            self._load_file(file_path)

    def _load_file(self, file_path: str):
        """Load and validate audio file."""
        # Validate file
        is_valid, error_msg = self.audio_utils.validate_audio_file(file_path)

        if not is_valid:
            self._show_error(error_msg)
            return

        # Get file info
        try:
            info = self.audio_utils.get_audio_info(file_path)
            self.selected_file = file_path

            # Update UI
            self.file_name_label.configure(text=f"📄 {Path(file_path).name}")
            self.file_info_label.configure(
                text=f"Format: {info['format']} | "
                     f"Duration: {info['duration_formatted']} | "
                     f"Size: {info['file_size_formatted']}"
            )

            self.info_frame.pack(fill="x", padx=10, pady=10)
            self.transcribe_btn.configure(state="normal")
            self.clear_btn.configure(state="normal")

            # Update drop zone appearance
            self.drop_zone.configure(border_color="green")

        except Exception as e:
            self._show_error(f"Error loading file: {str(e)}")

    def _clear_file(self):
        """Clear selected file."""
        self.selected_file = None
        self.info_frame.pack_forget()
        self.transcribe_btn.configure(state="disabled")
        self.clear_btn.configure(state="disabled")
        self.drop_zone.configure(border_color="gray")

    def _transcribe(self):
        """Trigger transcription of selected file."""
        if self.selected_file:
            self.on_transcribe_callback(self.selected_file)

    def set_transcript(self, transcript: str):
        """Set transcript in display (called after transcription completes)."""
        self.current_transcript = transcript

        # Update feedback panel with transcript
        self.feedback_panel.set_transcript(transcript)

        # Auto-organize if enabled
        settings = self.settings_manager.load_settings()
        if settings.feedback.auto_organize and self.feedback_panel.current_rubric:
            self.feedback_panel._organize_feedback()

    def _show_error(self, message: str):
        """Show error message in dialog."""
        from tkinter import messagebox
        messagebox.showerror("Error", message)
