"""Slicer-related data models."""

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class SlicerType(str, Enum):
    """Supported slicer types."""

    ORCASLICER = "orcaslicer"
    ORCA_FLASHFORGE = "orca-flashforge"


class SlicerInfo(BaseModel):
    """Information about a detected slicer installation."""

    name: SlicerType = Field(..., description="Slicer type identifier")
    display_name: str = Field(..., description="Human-readable slicer name")
    config_path: Path = Field(..., description="Path to slicer config directory")
    exists: bool = Field(..., description="Whether the slicer is installed")
    version: Optional[str] = Field(None, description="Detected slicer version")
    conf_file: Optional[Path] = Field(None, description="Path to main .conf file")
    user_dir: Optional[Path] = Field(None, description="Path to user profiles directory")
    custom_scripts_dir: Optional[Path] = Field(
        None, description="Path to custom scripts directory (if exists)"
    )

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        arbitrary_types_allowed = True

    def is_valid(self) -> bool:
        """Check if slicer installation is valid and has required files."""
        if not self.exists:
            return False
        if not self.conf_file or not self.conf_file.exists():
            return False
        if not self.user_dir or not self.user_dir.exists():
            return False
        return True
