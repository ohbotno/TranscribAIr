"""
Feedback organization system using LLM providers.
Handles organizing transcripts according to rubric criteria.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from dataclasses import dataclass

from core.rubric import Rubric
from core.settings import LLMSettings


@dataclass
class OrganizedFeedback:
    """Structured feedback organized by rubric criteria."""
    rubric_name: str
    criterion_feedback: Dict[str, str]  # criterion_name -> feedback text
    summary: str = ""
    raw_transcript: str = ""

    def to_markdown(self) -> str:
        """Convert organized feedback to markdown format."""
        lines = [f"# Feedback: {self.rubric_name}", ""]

        if self.summary:
            lines.extend(["## Summary", self.summary, ""])

        lines.append("## Detailed Feedback")
        lines.append("")

        for criterion, feedback in self.criterion_feedback.items():
            lines.append(f"### {criterion}")
            lines.append(feedback)
            lines.append("")

        if self.raw_transcript:
            lines.extend(["---", "## Raw Transcript", self.raw_transcript])

        return "\n".join(lines)

    def to_plain_text(self) -> str:
        """Convert organized feedback to plain text format."""
        lines = [f"FEEDBACK: {self.rubric_name}", "=" * 60, ""]

        if self.summary:
            lines.extend(["SUMMARY:", self.summary, ""])

        lines.append("DETAILED FEEDBACK:")
        lines.append("-" * 60)

        for criterion, feedback in self.criterion_feedback.items():
            lines.append(f"\n{criterion}:")
            lines.append(feedback)

        if self.raw_transcript:
            lines.extend(["", "=" * 60, "RAW TRANSCRIPT:", self.raw_transcript])

        return "\n".join(lines)


@dataclass
class StructuredFeedback:
    """Structured feedback in four-section format (Overall Summary, Strengths, Areas for Improvement, Closing Comment)."""
    rubric_name: str
    feedback_text: str  # The complete structured feedback
    raw_transcript: str = ""

    def to_markdown(self) -> str:
        """Convert structured feedback to markdown format."""
        lines = [f"# Feedback: {self.rubric_name}", ""]
        lines.append(self.feedback_text)

        if self.raw_transcript:
            lines.extend(["", "---", "## Raw Transcript", self.raw_transcript])

        return "\n".join(lines)

    def to_plain_text(self) -> str:
        """Convert structured feedback to plain text format."""
        lines = [f"FEEDBACK: {self.rubric_name}", "=" * 60, ""]
        lines.append(self.feedback_text)

        if self.raw_transcript:
            lines.extend(["", "=" * 60, "RAW TRANSCRIPT:", self.raw_transcript])

        return "\n".join(lines)


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def organize_feedback(
        self,
        transcript: str,
        rubric: Rubric,
        detail_level: str = "detailed"
    ) -> Optional[OrganizedFeedback]:
        """
        Organize transcript feedback according to rubric criteria.

        Args:
            transcript: Raw transcript text
            rubric: Rubric to organize feedback by
            detail_level: "brief" or "detailed"

        Returns:
            OrganizedFeedback object or None if failed
        """
        pass

    @abstractmethod
    def organize_structured_feedback(
        self,
        transcript: str,
        rubric: Rubric,
        instruction_prompt: str
    ) -> Optional[StructuredFeedback]:
        """
        Convert transcript to structured feedback using custom instruction prompt.

        Args:
            transcript: Raw transcript text
            rubric: Rubric for alignment
            instruction_prompt: Custom instruction prompt template

        Returns:
            StructuredFeedback object or None if failed
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is available and configured."""
        pass

    def _build_prompt(self, transcript: str, rubric: Rubric, detail_level: str) -> str:
        """Build the prompt for organizing feedback."""
        criteria_list = "\n".join([
            f"- {c.name}: {c.description}" for c in rubric.criteria
        ])

        detail_instruction = (
            "Provide concise, actionable feedback for each criterion."
            if detail_level == "brief"
            else "Provide detailed, constructive feedback for each criterion with specific examples from the transcript."
        )

        prompt = f"""You are organizing verbal feedback that a teacher has recorded. Your task is to organize this feedback according to the provided rubric criteria.

The feedback should be written in FIRST PERSON, as if the teacher is speaking directly to the student (use "I", "my observations", "I noticed", etc.).

RUBRIC: {rubric.name}
{rubric.description}

CRITERIA:
{criteria_list}

TEACHER'S VERBAL FEEDBACK (TRANSCRIPT):
{transcript}

INSTRUCTIONS:
1. Analyze the transcript and identify feedback related to each rubric criterion
2. {detail_instruction}
3. If the teacher didn't mention a specific criterion, note that it wasn't addressed
4. Write in FIRST PERSON perspective - as if the teacher is speaking directly ("I think...", "I noticed...", "In my view...")
5. Maintain the teacher's conversational tone and specific comments
6. Provide a brief overall summary (2-3 sentences) in first person

OUTPUT FORMAT:
Return your response in the following JSON format:
{{
    "summary": "Brief overall summary in first person (e.g., 'I found your work...')",
    "criterion_feedback": {{
        "Criterion Name 1": "Feedback in first person for this criterion",
        "Criterion Name 2": "Feedback in first person for this criterion",
        ...
    }}
}}

IMPORTANT: All feedback must be written in first person, as if the teacher is speaking directly to the student.

Ensure all criterion names from the rubric are included in your response, even if the teacher didn't explicitly address them (in which case note "I didn't address this in my feedback" or similar).
"""
        return prompt

    def _build_structured_prompt(self, transcript: str, rubric: Rubric, instruction_prompt: str) -> str:
        """Build the prompt for structured feedback conversion."""
        # Build rubric text
        rubric_text = f"{rubric.name}\n{rubric.description}\n\nCriteria:\n"
        for criterion in rubric.criteria:
            rubric_text += f"- **{criterion.name}**: {criterion.description}\n"

        # Combine instruction prompt with inputs
        full_prompt = f"""{instruction_prompt}

---

RUBRIC:
{rubric_text}

TRANSCRIPT:
{transcript}
"""
        return full_prompt


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider."""

    def __init__(self, settings: LLMSettings):
        self.model = settings.ollama_model
        self.base_url = settings.ollama_base_url
        self._client = None

    def _get_client(self):
        """Lazy load Ollama client."""
        if self._client is None:
            try:
                import ollama
                self._client = ollama.Client(host=self.base_url)
            except ImportError:
                print("Ollama package not installed. Install with: pip install ollama")
                return None
        return self._client

    def is_available(self) -> bool:
        """Check if Ollama is available."""
        client = self._get_client()
        if not client:
            return False

        try:
            # Try to list models to verify connection
            client.list()
            return True
        except Exception as e:
            print(f"Ollama not available: {e}")
            return False

    def organize_feedback(
        self,
        transcript: str,
        rubric: Rubric,
        detail_level: str = "detailed"
    ) -> Optional[OrganizedFeedback]:
        """Organize feedback using Ollama."""
        client = self._get_client()
        if not client:
            return None

        try:
            prompt = self._build_prompt(transcript, rubric, detail_level)

            response = client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                format="json"
            )

            import json
            result = json.loads(response['message']['content'])

            return OrganizedFeedback(
                rubric_name=rubric.name,
                criterion_feedback=result.get('criterion_feedback', {}),
                summary=result.get('summary', ''),
                raw_transcript=transcript
            )

        except Exception as e:
            print(f"Error organizing feedback with Ollama: {e}")
            # Re-raise to let UI handle the error display
            raise

    def organize_structured_feedback(
        self,
        transcript: str,
        rubric: Rubric,
        instruction_prompt: str
    ) -> Optional[StructuredFeedback]:
        """Convert transcript to structured feedback using Ollama."""
        client = self._get_client()
        if not client:
            return None

        try:
            prompt = self._build_structured_prompt(transcript, rubric, instruction_prompt)

            response = client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )

            feedback_text = response['message']['content']

            return StructuredFeedback(
                rubric_name=rubric.name,
                feedback_text=feedback_text,
                raw_transcript=transcript
            )

        except Exception as e:
            print(f"Error organizing structured feedback with Ollama: {e}")
            raise


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider."""

    def __init__(self, settings: LLMSettings):
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self._client = None

    def _get_client(self):
        """Lazy load OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                print("OpenAI package not installed. Install with: pip install openai")
                return None
        return self._client

    def is_available(self) -> bool:
        """Check if OpenAI is configured."""
        return bool(self.api_key) and self._get_client() is not None

    def organize_feedback(
        self,
        transcript: str,
        rubric: Rubric,
        detail_level: str = "detailed"
    ) -> Optional[OrganizedFeedback]:
        """Organize feedback using OpenAI."""
        client = self._get_client()
        if not client:
            return None

        try:
            prompt = self._build_prompt(transcript, rubric, detail_level)

            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)

            return OrganizedFeedback(
                rubric_name=rubric.name,
                criterion_feedback=result.get('criterion_feedback', {}),
                summary=result.get('summary', ''),
                raw_transcript=transcript
            )

        except Exception as e:
            print(f"Error organizing feedback with OpenAI: {e}")
            # Re-raise to let UI handle the error display
            raise

    def organize_structured_feedback(
        self,
        transcript: str,
        rubric: Rubric,
        instruction_prompt: str
    ) -> Optional[StructuredFeedback]:
        """Convert transcript to structured feedback using OpenAI."""
        client = self._get_client()
        if not client:
            return None

        try:
            prompt = self._build_structured_prompt(transcript, rubric, instruction_prompt)

            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )

            feedback_text = response.choices[0].message.content

            return StructuredFeedback(
                rubric_name=rubric.name,
                feedback_text=feedback_text,
                raw_transcript=transcript
            )

        except Exception as e:
            print(f"Error organizing structured feedback with OpenAI: {e}")
            raise


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API provider."""

    def __init__(self, settings: LLMSettings):
        self.api_key = settings.anthropic_api_key
        self.model = settings.anthropic_model
        self._client = None

    def _get_client(self):
        """Lazy load Anthropic client."""
        if self._client is None:
            try:
                from anthropic import Anthropic
                self._client = Anthropic(api_key=self.api_key)
            except ImportError:
                print("Anthropic package not installed. Install with: pip install anthropic")
                return None
        return self._client

    def is_available(self) -> bool:
        """Check if Anthropic is configured."""
        return bool(self.api_key) and self._get_client() is not None

    def organize_feedback(
        self,
        transcript: str,
        rubric: Rubric,
        detail_level: str = "detailed"
    ) -> Optional[OrganizedFeedback]:
        """Organize feedback using Anthropic Claude."""
        client = self._get_client()
        if not client:
            return None

        try:
            prompt = self._build_prompt(transcript, rubric, detail_level)

            # Claude doesn't have native JSON mode, so we'll parse the response
            response = client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            # Extract JSON from response
            content = response.content[0].text

            # Try to find JSON in the response
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = content[start:end]
                result = json.loads(json_str)
            else:
                print("Could not parse JSON from Claude response")
                return None

            return OrganizedFeedback(
                rubric_name=rubric.name,
                criterion_feedback=result.get('criterion_feedback', {}),
                summary=result.get('summary', ''),
                raw_transcript=transcript
            )

        except Exception as e:
            print(f"Error organizing feedback with Anthropic: {e}")
            # Re-raise to let UI handle the error display
            raise

    def organize_structured_feedback(
        self,
        transcript: str,
        rubric: Rubric,
        instruction_prompt: str
    ) -> Optional[StructuredFeedback]:
        """Convert transcript to structured feedback using Anthropic Claude."""
        client = self._get_client()
        if not client:
            return None

        try:
            prompt = self._build_structured_prompt(transcript, rubric, instruction_prompt)

            response = client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )

            feedback_text = response.content[0].text

            return StructuredFeedback(
                rubric_name=rubric.name,
                feedback_text=feedback_text,
                raw_transcript=transcript
            )

        except Exception as e:
            print(f"Error organizing structured feedback with Anthropic: {e}")
            raise


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter API provider - unified API for multiple LLM models."""

    def __init__(self, settings: LLMSettings):
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model
        self._client = None

    def _get_client(self):
        """Lazy load OpenAI-compatible client for OpenRouter."""
        if self._client is None:
            try:
                from openai import OpenAI
                # OpenRouter uses OpenAI-compatible API
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
            except ImportError:
                print("OpenAI package not installed. Install with: pip install openai")
                return None
        return self._client

    def is_available(self) -> bool:
        """Check if OpenRouter is configured."""
        return bool(self.api_key) and self._get_client() is not None

    def organize_feedback(
        self,
        transcript: str,
        rubric: Rubric,
        detail_level: str = "detailed"
    ) -> Optional[OrganizedFeedback]:
        """Organize feedback using OpenRouter."""
        client = self._get_client()
        if not client:
            return None

        try:
            prompt = self._build_prompt(transcript, rubric, detail_level)

            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)

            return OrganizedFeedback(
                rubric_name=rubric.name,
                criterion_feedback=result.get('criterion_feedback', {}),
                summary=result.get('summary', ''),
                raw_transcript=transcript
            )

        except Exception as e:
            print(f"Error organizing feedback with OpenRouter: {e}")
            # Re-raise to let UI handle the error display
            raise

    def organize_structured_feedback(
        self,
        transcript: str,
        rubric: Rubric,
        instruction_prompt: str
    ) -> Optional[StructuredFeedback]:
        """Convert transcript to structured feedback using OpenRouter."""
        client = self._get_client()
        if not client:
            return None

        try:
            prompt = self._build_structured_prompt(transcript, rubric, instruction_prompt)

            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )

            feedback_text = response.choices[0].message.content

            return StructuredFeedback(
                rubric_name=rubric.name,
                feedback_text=feedback_text,
                raw_transcript=transcript
            )

        except Exception as e:
            print(f"Error organizing structured feedback with OpenRouter: {e}")
            raise


class FeedbackOrganizer:
    """Main feedback organization coordinator."""

    def __init__(self, settings: LLMSettings):
        self.settings = settings
        self.providers = {
            "ollama": OllamaProvider(settings),
            "openai": OpenAIProvider(settings),
            "anthropic": AnthropicProvider(settings),
            "openrouter": OpenRouterProvider(settings)
        }

    def get_provider(self, provider_name: Optional[str] = None) -> Optional[BaseLLMProvider]:
        """Get the specified provider or the configured default."""
        provider_name = provider_name or self.settings.provider
        return self.providers.get(provider_name)

    def organize_feedback(
        self,
        transcript: str,
        rubric: Rubric,
        detail_level: str = "detailed",
        provider_name: Optional[str] = None
    ) -> Optional[OrganizedFeedback]:
        """
        Organize feedback using the specified or default provider.

        Args:
            transcript: Raw transcript text
            rubric: Rubric to organize feedback by
            detail_level: "brief" or "detailed"
            provider_name: Optional override for provider

        Returns:
            OrganizedFeedback or None if failed
        """
        provider = self.get_provider(provider_name)
        if not provider:
            print(f"Provider '{provider_name or self.settings.provider}' not available")
            return None

        if not provider.is_available():
            print(f"Provider '{provider_name or self.settings.provider}' is not available or configured")
            return None

        return provider.organize_feedback(transcript, rubric, detail_level)

    def organize_structured_feedback(
        self,
        transcript: str,
        rubric: Rubric,
        instruction_prompt: str,
        provider_name: Optional[str] = None
    ) -> Optional[StructuredFeedback]:
        """
        Convert transcript to structured feedback using custom instruction prompt.

        Args:
            transcript: Raw transcript text
            rubric: Rubric for alignment
            instruction_prompt: Custom instruction prompt template
            provider_name: Optional override for provider

        Returns:
            StructuredFeedback or None if failed
        """
        provider = self.get_provider(provider_name)
        if not provider:
            print(f"Provider '{provider_name or self.settings.provider}' not available")
            return None

        if not provider.is_available():
            print(f"Provider '{provider_name or self.settings.provider}' is not available or configured")
            return None

        return provider.organize_structured_feedback(transcript, rubric, instruction_prompt)

    def list_available_providers(self) -> List[str]:
        """List all available and configured providers."""
        return [
            name for name, provider in self.providers.items()
            if provider.is_available()
        ]
