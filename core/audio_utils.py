"""
Audio file utilities for format conversion and validation.
Uses pydub for handling multiple audio formats.
"""
import os
from pathlib import Path
from typing import Optional, Tuple
from pydub import AudioSegment
from pydub.utils import mediainfo


class AudioUtils:
    """Utilities for audio file operations."""

    SUPPORTED_FORMATS = {
        '.mp3': 'MP3',
        '.wav': 'WAV',
        '.m4a': 'M4A',
        '.flac': 'FLAC',
        '.ogg': 'OGG',
        '.aac': 'AAC',
        '.wma': 'WMA',
        '.opus': 'OPUS'
    }

    @staticmethod
    def is_supported_format(file_path: str) -> bool:
        """
        Check if audio format is supported.

        Args:
            file_path: Path to audio file

        Returns:
            True if format is supported
        """
        ext = Path(file_path).suffix.lower()
        return ext in AudioUtils.SUPPORTED_FORMATS

    @staticmethod
    def get_audio_info(file_path: str) -> dict:
        """
        Get information about an audio file.

        Args:
            file_path: Path to audio file

        Returns:
            Dictionary with audio info (duration, format, size, etc.)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        # Get file info
        file_size = os.path.getsize(file_path)
        ext = Path(file_path).suffix.lower()

        try:
            # Load audio to get detailed info
            audio = AudioSegment.from_file(file_path)

            info = {
                'path': file_path,
                'format': AudioUtils.SUPPORTED_FORMATS.get(ext, 'Unknown'),
                'duration_seconds': len(audio) / 1000.0,
                'duration_formatted': AudioUtils._format_duration(len(audio) / 1000.0),
                'sample_rate': audio.frame_rate,
                'channels': audio.channels,
                'file_size_bytes': file_size,
                'file_size_formatted': AudioUtils._format_file_size(file_size),
                'bitrate': audio.frame_rate * audio.frame_width * audio.channels * 8
            }

            return info

        except Exception as e:
            raise RuntimeError(f"Error reading audio file: {str(e)}")

    @staticmethod
    def convert_to_wav(
        input_path: str,
        output_path: Optional[str] = None,
        sample_rate: int = 16000
    ) -> str:
        """
        Convert audio file to WAV format optimized for Whisper.

        Args:
            input_path: Path to input audio file
            output_path: Optional output path (defaults to temp directory)
            sample_rate: Target sample rate (16000 is optimal for Whisper)

        Returns:
            Path to converted WAV file
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Determine output path
        if output_path is None:
            input_file = Path(input_path)
            output_path = str(input_file.parent / f"{input_file.stem}_converted.wav")

        try:
            # Load audio file
            audio = AudioSegment.from_file(input_path)

            # Convert to mono and set sample rate
            audio = audio.set_channels(1)
            audio = audio.set_frame_rate(sample_rate)

            # Export as WAV
            audio.export(
                output_path,
                format='wav',
                parameters=["-ac", "1"]  # Ensure mono
            )

            return output_path

        except Exception as e:
            raise RuntimeError(f"Error converting audio file: {str(e)}")

    @staticmethod
    def validate_audio_file(file_path: str) -> Tuple[bool, str]:
        """
        Validate audio file can be loaded and processed.

        Args:
            file_path: Path to audio file

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not os.path.exists(file_path):
            return False, "File does not exist"

        if not AudioUtils.is_supported_format(file_path):
            ext = Path(file_path).suffix.lower()
            supported = ', '.join(AudioUtils.SUPPORTED_FORMATS.keys())
            return False, f"Unsupported format '{ext}'. Supported: {supported}"

        try:
            # Try to load audio
            audio = AudioSegment.from_file(file_path)

            # Check duration (at least 0.1 seconds)
            if len(audio) < 100:
                return False, "Audio file is too short (minimum 0.1 seconds)"

            return True, ""

        except Exception as e:
            return False, f"Cannot load audio file: {str(e)}"

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format duration as MM:SS or HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def _format_file_size(bytes_size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"
