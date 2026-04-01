from pydantic import BaseModel, Field, field_serializer, field_validator
from datetime import datetime
from typing import Any, List, Optional
from enum import Enum
import uuid

# Constants
MAX_TITLE_LENGTH = 200
MAX_INGREDIENTS = 50


def _normalize_instruction_steps(value: Any) -> List[str]:
    if value is None:
        return []

    if isinstance(value, str):
        return [step.strip() for step in value.replace("\r\n", "\n").split("\n\n") if step.strip()]

    if isinstance(value, list):
        return [str(step).strip() for step in value if str(step).strip()]

    return value


def _normalize_optional_text(value: Any) -> Optional[str]:
    if value is None:
        return None

    text = str(value).strip()
    return text or None

class DifficultyLevel(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium" 
    HARD = "Hard"

class Recipe(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str 
    description: str
    ingredients: List[str]
    instructions: List[str]
    tags: List[str] = Field(default_factory=list)
    region: Optional[str] = None
    cuisine: Optional[str] = None
    difficulty: DifficultyLevel
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @field_validator("instructions", mode="before")
    @classmethod
    def normalize_instructions(cls, value: Any) -> List[str]:
        return _normalize_instruction_steps(value)

    @field_validator("region", "cuisine", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Any) -> Optional[str]:
        return _normalize_optional_text(value)


    @field_serializer("created_at", "updated_at")
    def serialize_datetimes(self, value: datetime) -> str:
        return value.isoformat()


class RecipeCreate(BaseModel):
    title: str
    description: str
    ingredients: List[str]
    instructions: List[str]
    tags: List[str] = Field(default_factory=list)
    region: Optional[str] = None
    cuisine: Optional[str] = None
    difficulty: DifficultyLevel

    @field_validator("instructions", mode="before")
    @classmethod
    def normalize_instructions(cls, value: Any) -> List[str]:
        return _normalize_instruction_steps(value)

    @field_validator("region", "cuisine", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Any) -> Optional[str]:
        return _normalize_optional_text(value)


class RecipeUpdate(BaseModel):
    title: str
    description: str
    ingredients: List[str]
    instructions: List[str]
    tags: List[str]
    region: Optional[str] = None
    cuisine: Optional[str] = None
    difficulty: DifficultyLevel

    @field_validator("instructions", mode="before")
    @classmethod
    def normalize_instructions(cls, value: Any) -> List[str]:
        return _normalize_instruction_steps(value)

    @field_validator("region", "cuisine", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Any) -> Optional[str]:
        return _normalize_optional_text(value)
