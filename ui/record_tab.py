"""
Record tab for live audio recording with feedback support.
Handles microphone input, visualization, and recording controls.
"""
import customtkinter as ctk
from typing import Callable, Optional
from pathlib import Path
import threading
import time

from core import AudioRecorder
from core.rubric import RubricManager
from core.settings import SettingsManager
from core.feedback import FeedbackOrganizer
from .feedback_panel import FeedbackPanel
from .mini_recorder import MiniRecorder


class RecordTab(ctk.CTkFrame):
    """Record tab UI component with minimized recording and full-width feedback."""

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

        self.recorder = AudioRecorder()
        self.is_recording = False
        self.recorded_file: Optional[str] = None
        self.current_transcript = ""
        self.mini_recorder_window: Optional[MiniRecorder] = None

        self._create_ui()

        # Pack the tab frame into its parent
        self.pack(fill="both", expand=True)

    def _create_ui(self):
        """Create record tab UI with compact controls and full-width feedback."""
        # Main container
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Top section - compact recording controls
        control_section = ctk.CTkFrame(main_container, height=100)
        control_section.pack(fill="x", pady=(0, 10))
        control_section.pack_propagate(False)

        # Device selector row
        device_frame = ctk.CTkFrame(control_section)
        device_frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(
            device_frame,
            text="Microphone:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(side="left", padx=(0, 10))

        # Get available devices
        devices = self.recorder.get_available_devices()
        device_names = [f"{d['name']}" for d in devices]
        self.device_indices = [d['index'] for d in devices]

        if device_names:
            default_device = device_names[0]
        else:
            device_names = ["No microphone detected"]
            default_device = device_names[0]

        self.device_var = ctk.StringVar(value=default_device)
        self.device_dropdown = ctk.CTkOptionMenu(
            device_frame,
            variable=self.device_var,
            values=device_names,
            width=400
        )
        self.device_dropdown.pack(side="left", fill="x", expand=True)

        # Recording buttons row
        button_frame = ctk.CTkFrame(control_section)
        button_frame.pack(fill="x", padx=10, pady=5)

        self.record_btn = ctk.CTkButton(
            button_frame,
            text="⏺ Start Recording",
            command=self._toggle_recording,
            width=180,
            height=40,
            fg_color="red",
            hover_color="darkred",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.record_btn.pack(side="left", padx=5)

        self.transcribe_btn = ctk.CTkButton(
            button_frame,
            text="Transcribe",
            command=self._transcribe,
            width=140,
            height=40,
            state="disabled"
        )
        self.transcribe_btn.pack(side="left", padx=5)

        self.new_btn = ctk.CTkButton(
            button_frame,
            text="New Recording",
            command=self._new_recording,
            width=140,
            height=40,
            fg_color="gray60",
            state="disabled"
        )
        self.new_btn.pack(side="left", padx=5)

        # Status label
        self.status_label = ctk.CTkLabel(
            button_frame,
            text="Ready to record",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.status_label.pack(side="left", padx=20)

        # Full-width feedback panel
        self.feedback_panel = FeedbackPanel(
            main_container,
            self.rubric_manager,
            self.settings_manager,
            self.feedback_organizer
        )
        self.feedback_panel.pack(fill="both", expand=True)

    def _toggle_recording(self):
        """Start or stop recording."""
        if not self.is_recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        """Start audio recording."""
        try:
            # Get selected device index
            device_idx = None
            if self.device_indices:
                selected_idx = self.device_dropdown.cget("values").index(self.device_var.get())
                device_idx = self.device_indices[selected_idx]

            # Start recorder
            self.recorder.start_recording(
                device_index=device_idx,
                level_callback=self._update_level
            )

            self.is_recording = True

            # Update UI
            self.record_btn.configure(state="disabled")
            self.device_dropdown.configure(state="disabled")
            self.transcribe_btn.configure(state="disabled")
            self.new_btn.configure(state="disabled")
            self.status_label.configure(text="Recording in progress...")

            # Check if we should minimize
            settings = self.settings_manager.load_settings()
            if settings.ui.minimize_while_recording:
                # Minimize main window first
                self.winfo_toplevel().iconify()
                # Small delay to ensure main window is minimized
                self.after(100, self._show_mini_recorder)

        except Exception as e:
            self._show_error(f"Error starting recording: {str(e)}")

    def _show_mini_recorder(self):
        """Show mini recorder window after main window is minimized."""
        # Get the root window instead of self for parent
        root = self.winfo_toplevel()
        self.mini_recorder_window = MiniRecorder(
            root,
            on_stop=self._stop_recording_from_mini,
            initial_device=self.device_var.get()
        )
        self.mini_recorder_window.start_recording()

    def _stop_recording_from_mini(self):
        """Stop recording from minimized window."""
        self._stop_recording()

    def _stop_recording(self):
        """Stop audio recording."""
        try:
            # Create temp directory
            temp_dir = Path.home() / ".transcribair" / "recordings"
            temp_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = temp_dir / f"recording_{timestamp}.wav"

            # Stop recording and save
            self.recorded_file = self.recorder.stop_recording(str(output_path))

            self.is_recording = False

            # Get elapsed time from mini recorder if it exists
            elapsed_time = 0
            if self.mini_recorder_window:
                try:
                    elapsed_time = self.mini_recorder_window.get_elapsed_time()
                    if self.mini_recorder_window.winfo_exists():
                        self.mini_recorder_window.destroy()
                except Exception as e:
                    print(f"Error closing mini recorder: {e}")
                finally:
                    self.mini_recorder_window = None

            # Restore main window if it was minimized
            self.winfo_toplevel().deiconify()
            self.winfo_toplevel().lift()
            self.winfo_toplevel().focus_force()

            # Update UI
            self.record_btn.configure(
                text="⏺ Start Recording",
                state="normal"
            )
            self.status_label.configure(text=f"Recording saved ({self._format_time(elapsed_time)})")
            self.device_dropdown.configure(state="normal")
            self.transcribe_btn.configure(state="normal")
            self.new_btn.configure(state="normal")

        except Exception as e:
            self.is_recording = False
            if self.mini_recorder_window:
                try:
                    if self.mini_recorder_window.winfo_exists():
                        self.mini_recorder_window.destroy()
                except:
                    pass
                finally:
                    self.mini_recorder_window = None
            self.winfo_toplevel().deiconify()
            self._show_error(f"Error stopping recording: {str(e)}")

    def _new_recording(self):
        """Clear current recording and start fresh."""
        self.recorded_file = None
        self.current_transcript = ""
        self.feedback_panel.clear()
        self.record_btn.configure(state="normal")
        self.transcribe_btn.configure(state="disabled")
        self.new_btn.configure(state="disabled")
        self.status_label.configure(text="Ready to record")

    def _transcribe(self):
        """Trigger transcription of recorded audio."""
        if self.recorded_file:
            # Call the main window's transcribe method
            self.on_transcribe_callback(self.recorded_file)

    def set_transcript(self, transcript: str):
        """Set transcript in display (called after transcription completes)."""
        self.current_transcript = transcript

        # Update feedback panel with transcript
        self.feedback_panel.set_transcript(transcript)

        # Auto-organize if enabled
        settings = self.settings_manager.load_settings()
        if settings.feedback.auto_organize and self.feedback_panel.current_rubric:
            self.feedback_panel._organize_feedback()

    def _update_level(self, level: float):
        """Update audio level meter in mini recorder if it exists."""
        if self.mini_recorder_window:
            self.mini_recorder_window.update_level(level)

    @staticmethod
    def _format_time(seconds: int) -> str:
        """Format seconds as MM:SS."""
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def _show_error(self, message: str):
        """Show error message in dialog."""
        from tkinter import messagebox
        messagebox.showerror("Error", message)
