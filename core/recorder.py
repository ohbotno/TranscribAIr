"""
Audio recording functionality using sounddevice.
Handles microphone input and WAV file generation.
"""
import queue
import threading
from pathlib import Path
from typing import Optional, Callable
import numpy as np
import sounddevice as sd
import soundfile as sf


class AudioRecorder:
    """Manages audio recording from microphone."""

    def __init__(self, sample_rate: int = 16000):
        """
        Initialize recorder.

        Args:
            sample_rate: Sample rate in Hz (16000 is optimal for Whisper)
        """
        self.sample_rate = sample_rate
        self.channels = 1  # Mono audio
        self.is_recording = False
        self.is_paused = False
        self.audio_queue = queue.Queue()
        self.recorded_frames = []
        self.stream: Optional[sd.InputStream] = None
        self.record_thread: Optional[threading.Thread] = None

    def get_available_devices(self) -> list[dict]:
        """
        Get list of available input audio devices.

        Returns:
            List of device info dictionaries
        """
        devices = sd.query_devices()
        input_devices = []

        for idx, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append({
                    'index': idx,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': device['default_samplerate']
                })

        return input_devices

    def start_recording(
        self,
        device_index: Optional[int] = None,
        level_callback: Optional[Callable[[float], None]] = None
    ) -> None:
        """
        Start recording audio.

        Args:
            device_index: Optional specific input device to use
            level_callback: Optional callback for audio level (0.0 to 1.0)
        """
        if self.is_recording:
            raise RuntimeError("Already recording")

        self.is_recording = True
        self.is_paused = False
        self.recorded_frames = []
        self.audio_queue = queue.Queue()

        def audio_callback(indata, frames, time, status):
            """Callback for audio stream."""
            if status:
                print(f"Audio callback status: {status}")

            if not self.is_paused:
                # Add to queue for processing
                self.audio_queue.put(indata.copy())

                # Calculate audio level for visualization
                if level_callback:
                    level = np.abs(indata).mean()
                    level_callback(float(level))

        # Start audio stream
        self.stream = sd.InputStream(
            device=device_index,
            channels=self.channels,
            samplerate=self.sample_rate,
            callback=audio_callback,
            blocksize=1024
        )
        self.stream.start()

        # Start processing thread
        self.record_thread = threading.Thread(target=self._process_audio, daemon=True)
        self.record_thread.start()

    def pause_recording(self) -> None:
        """Pause recording (can be resumed)."""
        if not self.is_recording:
            raise RuntimeError("Not recording")
        self.is_paused = True

    def resume_recording(self) -> None:
        """Resume paused recording."""
        if not self.is_recording:
            raise RuntimeError("Not recording")
        self.is_paused = False

    def stop_recording(self, output_path: str) -> str:
        """
        Stop recording and save to file.

        Args:
            output_path: Path to save WAV file

        Returns:
            Path to saved file
        """
        if not self.is_recording:
            raise RuntimeError("Not recording")

        # Signal stop
        self.is_recording = False

        # Stop stream
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        # Wait for processing thread
        if self.record_thread:
            self.record_thread.join(timeout=2.0)

        # Combine all recorded frames
        if not self.recorded_frames:
            raise RuntimeError("No audio data recorded")

        audio_data = np.concatenate(self.recorded_frames, axis=0)

        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save to WAV file
        sf.write(
            str(output_path),
            audio_data,
            self.sample_rate,
            subtype='PCM_16'
        )

        return str(output_path)

    def _process_audio(self) -> None:
        """Process audio from queue (runs in background thread)."""
        while self.is_recording:
            try:
                # Get audio data from queue with timeout
                data = self.audio_queue.get(timeout=0.1)
                self.recorded_frames.append(data)
            except queue.Empty:
                continue

    def get_duration(self) -> float:
        """
        Get current recording duration in seconds.

        Returns:
            Duration in seconds
        """
        if not self.recorded_frames:
            return 0.0

        total_frames = sum(len(frame) for frame in self.recorded_frames)
        return total_frames / self.sample_rate

    def cancel_recording(self) -> None:
        """Cancel recording without saving."""
        if not self.is_recording:
            return

        self.is_recording = False

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        if self.record_thread:
            self.record_thread.join(timeout=2.0)

        self.recorded_frames = []
