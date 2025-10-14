"""
Application settings management.
Handles user preferences and configuration.
"""
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict
from enum import Enum


class LLMProvider(Enum):
    """Available LLM providers."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"


@dataclass
class LLMSettings:
    """Settings for LLM integration."""
    provider: str = LLMProvider.OLLAMA.value
    ollama_model: str = "llama2"
    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-haiku-20240307"
    openrouter_api_key: str = ""
    openrouter_model: str = "qwen/qwen-2.5-7b-instruct:free"  # More reliable free model

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'LLMSettings':
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class FeedbackSettings:
    """Settings for feedback organization."""
    auto_organize: bool = False
    default_rubric: str = ""
    last_selected_rubric: str = ""  # Persist last selected rubric
    include_raw_transcript: bool = False  # Changed default to False
    feedback_detail_level: str = "detailed"  # "brief" or "detailed"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'FeedbackSettings':
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class UISettings:
    """Settings for UI preferences."""
    minimize_while_recording: bool = True
    show_transcript_by_default: bool = False

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'UISettings':
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class AppSettings:
    """Complete application settings."""
    llm: LLMSettings
    feedback: FeedbackSettings
    ui: UISettings

    def to_dict(self) -> dict:
        return {
            'llm': self.llm.to_dict(),
            'feedback': self.feedback.to_dict(),
            'ui': self.ui.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AppSettings':
        return cls(
            llm=LLMSettings.from_dict(data.get('llm', {})),
            feedback=FeedbackSettings.from_dict(data.get('feedback', {})),
            ui=UISettings.from_dict(data.get('ui', {}))
        )

    @classmethod
    def default(cls) -> 'AppSettings':
        """Create default settings."""
        return cls(
            llm=LLMSettings(),
            feedback=FeedbackSettings(),
            ui=UISettings()
        )


class SettingsManager:
    """Manages application settings storage and retrieval."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize settings manager."""
        if config_dir is None:
            config_dir = Path.home() / ".transcribair"

        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "settings.json"

    def load_settings(self) -> AppSettings:
        """Load settings from disk, or return defaults if not found."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return AppSettings.from_dict(data)
        except Exception as e:
            print(f"Error loading settings: {e}")

        return AppSettings.default()

    def save_settings(self, settings: AppSettings) -> bool:
        """Save settings to disk."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    def reset_to_defaults(self) -> AppSettings:
        """Reset settings to defaults and save."""
        settings = AppSettings.default()
        self.save_settings(settings)
        return settings

    def update_llm_settings(self, **kwargs) -> bool:
        """Update specific LLM settings."""
        settings = self.load_settings()
        for key, value in kwargs.items():
            if hasattr(settings.llm, key):
                setattr(settings.llm, key, value)
        return self.save_settings(settings)

    def update_feedback_settings(self, **kwargs) -> bool:
        """Update specific feedback settings."""
        settings = self.load_settings()
        for key, value in kwargs.items():
            if hasattr(settings.feedback, key):
                setattr(settings.feedback, key, value)
        return self.save_settings(settings)
