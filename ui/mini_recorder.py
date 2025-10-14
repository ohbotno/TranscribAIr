"""
Minimized recording widget for compact recording mode.
Floating window showing only essential recording controls.
"""
import customtkinter as ctk
from typing import Callable, Optional


class MiniRecorder(ctk.CTkToplevel):
    """Minimized floating recording widget."""

    def __init__(
        self,
        parent,
        on_stop: Callable[[], None],
        initial_device: str = ""
    ):
        super().__init__(parent)

        self.on_stop_callback = on_stop
        self.is_recording = False
        self.elapsed_time = 0
        self.timer_running = False

        # Window configuration
        self.title("Recording...")
        self.geometry("340x220")
        self.resizable(False, False)

        # Keep on top and make independent
        self.attributes('-topmost', True)
        self.transient()  # Make it independent from parent

        # Prevent window from being closed by X button (force use of Stop button)
        self.protocol("WM_DELETE_WINDOW", self._on_stop)

        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (340 // 2)
        y = (self.winfo_screenheight() // 2) - (220 // 2)
        self.geometry(f"+{x}+{y}")

        self._create_ui()

        # Focus the window
        self.lift()
        self.focus_force()

    def _create_ui(self):
        """Create minimized recording UI."""
        # Main container
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Recording indicator
        self.indicator_label = ctk.CTkLabel(
            container,
            text="🔴",
            font=ctk.CTkFont(size=36)
        )
        self.indicator_label.pack(pady=(2, 0))

        # Status text
        self.status_label = ctk.CTkLabel(
            container,
            text="Recording in progress...",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(pady=1)

        # Timer
        self.timer_label = ctk.CTkLabel(
            container,
            text="00:00",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.timer_label.pack(pady=3)

        # Level meter
        level_frame = ctk.CTkFrame(container)
        level_frame.pack(pady=3, fill="x", padx=15)

        ctk.CTkLabel(
            level_frame,
            text="Level:",
            font=ctk.CTkFont(size=9)
        ).pack(side="left", padx=(0, 5))

        self.level_bar = ctk.CTkProgressBar(
            level_frame,
            height=8
        )
        self.level_bar.pack(side="left", fill="x", expand=True)
        self.level_bar.set(0)

        # Stop button - IMPORTANT: Make this very visible
        self.stop_btn = ctk.CTkButton(
            container,
            text="⏹ Stop Recording",
            command=self._on_stop,
            height=38,
            fg_color="red",
            hover_color="darkred",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.stop_btn.pack(pady=(8, 2), fill="x", padx=15)

    def start_recording(self):
        """Start recording and timer."""
        self.is_recording = True
        self.elapsed_time = 0
        self.timer_running = True
        self._update_timer()

    def _update_timer(self):
        """Update timer display."""
        if self.timer_running:
            self.elapsed_time += 1
            mins = self.elapsed_time // 60
            secs = self.elapsed_time % 60
            self.timer_label.configure(text=f"{mins:02d}:{secs:02d}")
            self.after(1000, self._update_timer)

    def update_level(self, level: float):
        """Update audio level meter (called from audio thread)."""
        if not self.winfo_exists() or not self.timer_running:
            return  # Window destroyed or recording stopped

        normalized = min(level * 10, 1.0)
        # Schedule UI update on main thread
        try:
            self.after(0, lambda: self._safe_update_level(normalized))
        except:
            pass  # Window might be destroyed

    def _safe_update_level(self, normalized: float):
        """Safely update level bar on main thread."""
        try:
            if self.winfo_exists() and self.timer_running:
                self.level_bar.set(normalized)
        except:
            pass  # Window destroyed

    def _on_stop(self):
        """Handle stop button click or window close."""
        if not self.is_recording:
            return  # Already stopped

        # Stop timer and recording FIRST to prevent further level updates
        self.timer_running = False
        self.is_recording = False

        # Disable button to prevent double-clicks
        try:
            self.stop_btn.configure(state="disabled", text="Stopping...")
        except:
            pass  # Window might be destroyed

        # Call the stop callback
        try:
            self.on_stop_callback()
        except Exception as e:
            print(f"Error in stop callback: {e}")
            # Still destroy the window even if callback fails
            try:
                self.destroy()
            except:
                pass

    def get_elapsed_time(self) -> int:
        """Get elapsed recording time in seconds."""
        return self.elapsed_time
