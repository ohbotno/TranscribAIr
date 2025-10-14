"""
Whisper transcription engine using faster-whisper.
Handles model management, downloads, and transcription.
"""
import os
from pathlib import Path
from typing import Optional, Callable, Iterator
from faster_whisper import WhisperModel


class Transcriber:
    """Manages Whisper model and transcription operations."""

    # Model sizes with approximate disk space requirements
    MODEL_SIZES = {
        "tiny": "~75 MB",
        "base": "~140 MB",
        "small": "~460 MB",
        "medium": "~1.5 GB",
        "large": "~2.9 GB"
    }

    def __init__(self, model_dir: Optional[str] = None):
        """
        Initialize transcriber.

        Args:
            model_dir: Directory to store models. Defaults to user's cache dir.
        """
        if model_dir is None:
            # Use user's home directory for model storage
            self.model_dir = str(Path.home() / ".transribair" / "models")
        else:
            self.model_dir = model_dir

        os.makedirs(self.model_dir, exist_ok=True)
        self.model: Optional[WhisperModel] = None
        self.current_model_size: Optional[str] = None

    def load_model(
        self,
        model_size: str = "base",
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> None:
        """
        Load or download a Whisper model.

        Args:
            model_size: One of "tiny", "base", "small", "medium", "large"
            progress_callback: Optional callback for progress updates
        """
        if model_size not in self.MODEL_SIZES:
            raise ValueError(f"Invalid model size. Choose from: {list(self.MODEL_SIZES.keys())}")

        # Don't reload if already loaded
        if self.model and self.current_model_size == model_size:
            if progress_callback:
                progress_callback(f"Model '{model_size}' already loaded")
            return

        if progress_callback:
            progress_callback(f"Loading model '{model_size}'...")

        try:
            # faster-whisper downloads to cache automatically
            # device="cpu" for CPU-only processing
            # compute_type="int8" for better CPU performance
            self.model = WhisperModel(
                model_size,
                device="cpu",
                compute_type="int8",
                download_root=self.model_dir
            )
            self.current_model_size = model_size

            if progress_callback:
                progress_callback(f"Model '{model_size}' loaded successfully")

        except Exception as e:
            if progress_callback:
                progress_callback(f"Error loading model: {str(e)}")
            raise

    def transcribe(
        self,
        audio_path: str,
        include_timestamps: bool = False,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> str:
        """
        Transcribe an audio file.

        Args:
            audio_path: Path to audio file
            include_timestamps: Whether to include timestamps in output
            progress_callback: Optional callback for progress updates

        Returns:
            Transcribed text
        """
        if self.model is None:
            raise RuntimeError("No model loaded. Call load_model() first.")

        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if progress_callback:
            progress_callback("Transcribing audio...")

        try:
            # Transcribe with English language
            segments, info = self.model.transcribe(
                audio_path,
                language="en",
                beam_size=5,
                vad_filter=True,  # Voice activity detection
            )

            # Build transcript
            transcript_parts = []

            for segment in segments:
                if include_timestamps:
                    # Format: [HH:MM:SS] text
                    start_time = self._format_timestamp(segment.start)
                    transcript_parts.append(f"[{start_time}] {segment.text.strip()}")
                else:
                    transcript_parts.append(segment.text.strip())

            transcript = "\n".join(transcript_parts)

            if progress_callback:
                progress_callback("Transcription complete!")

            return transcript

        except Exception as e:
            if progress_callback:
                progress_callback(f"Transcription error: {str(e)}")
            raise

    def transcribe_streaming(
        self,
        audio_path: str,
        include_timestamps: bool = False
    ) -> Iterator[str]:
        """
        Transcribe audio with streaming results (yields segments as they complete).

        Args:
            audio_path: Path to audio file
            include_timestamps: Whether to include timestamps

        Yields:
            Transcribed text segments
        """
        if self.model is None:
            raise RuntimeError("No model loaded. Call load_model() first.")

        segments, info = self.model.transcribe(
            audio_path,
            language="en",
            beam_size=5,
            vad_filter=True,
        )

        for segment in segments:
            if include_timestamps:
                start_time = self._format_timestamp(segment.start)
                yield f"[{start_time}] {segment.text.strip()}\n"
            else:
                yield f"{segment.text.strip()}\n"

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Format seconds as HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def get_available_models(self) -> dict[str, str]:
        """Get dictionary of available models with their sizes."""
        return self.MODEL_SIZES.copy()
