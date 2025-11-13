"""
Rubric management system for organizing feedback.
Handles creation, storage, and retrieval of assessment rubrics.
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class PerformanceLevel:
    """A performance level descriptor for a rubric criterion."""
    name: str  # e.g., "Poor", "Below Standard", "Excellent"
    score_range: str  # e.g., "<40%", "40-50%", "70-80%"
    description: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'PerformanceLevel':
        return cls(**data)


@dataclass
class RubricCriterion:
    """A single criterion in a rubric."""
    name: str
    description: str = ""  # For simple rubrics
    weight: float = 1.0  # Optional weighting for criteria
    performance_levels: Optional[List[PerformanceLevel]] = None  # For detailed rubrics

    def to_dict(self) -> dict:
        result = {
            'name': self.name,
            'description': self.description,
            'weight': self.weight
        }
        if self.performance_levels:
            result['performance_levels'] = [pl.to_dict() for pl in self.performance_levels]
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'RubricCriterion':
        # Handle performance levels if present
        performance_levels = None
        if 'performance_levels' in data and data['performance_levels']:
            performance_levels = [PerformanceLevel.from_dict(pl) for pl in data['performance_levels']]

        return cls(
            name=data['name'],
            description=data.get('description', ''),
            weight=data.get('weight', 1.0),
            performance_levels=performance_levels
        )


@dataclass
class Rubric:
    """A complete rubric with multiple criteria."""
    name: str
    criteria: List[RubricCriterion]
    description: str = ""
    created_at: str = ""
    modified_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.modified_at:
            self.modified_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'description': self.description,
            'criteria': [c.to_dict() for c in self.criteria],
            'created_at': self.created_at,
            'modified_at': self.modified_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Rubric':
        criteria = [RubricCriterion.from_dict(c) for c in data['criteria']]
        return cls(
            name=data['name'],
            criteria=criteria,
            description=data.get('description', ''),
            created_at=data.get('created_at', ''),
            modified_at=data.get('modified_at', '')
        )

    def update_modified(self):
        """Update the modified timestamp."""
        self.modified_at = datetime.now().isoformat()


class RubricManager:
    """Manages rubric storage and retrieval."""

    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize rubric manager with storage directory."""
        if storage_dir is None:
            storage_dir = Path.home() / ".transcribair" / "rubrics"

        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_rubric_path(self, rubric_name: str) -> Path:
        """Get the file path for a rubric."""
        # Sanitize filename
        safe_name = "".join(c for c in rubric_name if c.isalnum() or c in (' ', '-', '_')).strip()
        return self.storage_dir / f"{safe_name}.json"

    def save_rubric(self, rubric: Rubric) -> bool:
        """Save a rubric to storage."""
        try:
            rubric.update_modified()
            path = self._get_rubric_path(rubric.name)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(rubric.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving rubric: {e}")
            return False

    def load_rubric(self, rubric_name: str) -> Optional[Rubric]:
        """Load a rubric from storage."""
        try:
            path = self._get_rubric_path(rubric_name)
            if not path.exists():
                return None

            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return Rubric.from_dict(data)
        except Exception as e:
            print(f"Error loading rubric: {e}")
            return None

    def list_rubrics(self) -> List[str]:
        """List all available rubric names."""
        try:
            rubric_files = self.storage_dir.glob("*.json")
            return sorted([f.stem for f in rubric_files])
        except Exception as e:
            print(f"Error listing rubrics: {e}")
            return []

    def delete_rubric(self, rubric_name: str) -> bool:
        """Delete a rubric from storage."""
        try:
            path = self._get_rubric_path(rubric_name)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting rubric: {e}")
            return False

    def export_rubric(self, rubric: Rubric, export_path: Path) -> bool:
        """Export a rubric to a specific file path."""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(rubric.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting rubric: {e}")
            return False

    def import_rubric(self, import_path: Path) -> Optional[Rubric]:
        """Import a rubric from a file."""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            rubric = Rubric.from_dict(data)

            # Save to storage
            if self.save_rubric(rubric):
                return rubric
            return None
        except Exception as e:
            print(f"Error importing rubric: {e}")
            return None

    def rubric_exists(self, rubric_name: str) -> bool:
        """Check if a rubric exists."""
        return self._get_rubric_path(rubric_name).exists()


# Example rubric templates
def create_essay_rubric() -> Rubric:
    """Create a sample essay rubric template."""
    criteria = [
        RubricCriterion("Content", "Quality and relevance of ideas, arguments, and evidence", 2.0),
        RubricCriterion("Organization", "Structure, flow, and logical progression of ideas", 1.5),
        RubricCriterion("Grammar & Mechanics", "Spelling, punctuation, and sentence structure", 1.0),
        RubricCriterion("Style & Clarity", "Writing clarity, word choice, and tone", 1.0),
        RubricCriterion("Research & Citations", "Use of sources and proper citation format", 1.5),
    ]
    return Rubric(
        name="Essay Rubric",
        description="General rubric for essay assignments",
        criteria=criteria
    )


def create_presentation_rubric() -> Rubric:
    """Create a sample presentation rubric template."""
    criteria = [
        RubricCriterion("Content Knowledge", "Depth and accuracy of subject matter", 2.0),
        RubricCriterion("Organization", "Clear structure with intro, body, and conclusion", 1.5),
        RubricCriterion("Delivery", "Voice, pace, eye contact, and body language", 1.5),
        RubricCriterion("Visual Aids", "Quality and effectiveness of slides/materials", 1.0),
        RubricCriterion("Engagement", "Ability to engage audience and handle questions", 1.0),
    ]
    return Rubric(
        name="Presentation Rubric",
        description="General rubric for oral presentations",
        criteria=criteria
    )
