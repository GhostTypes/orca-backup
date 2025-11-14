"""Backup-related data models."""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


class FileEntry(BaseModel):
    """Information about a single file in a backup."""

    path: str = Field(..., description="Relative path within backup")
    size: int = Field(..., description="File size in bytes")
    sha256: str = Field(..., description="SHA256 checksum")


class BackupManifest(BaseModel):
    """Manifest describing backup contents and metadata."""

    version: str = Field(default="1.0", description="Manifest format version")
    created_at: datetime = Field(..., description="Backup creation timestamp")
    slicer: str = Field(..., description="Slicer type (orcaslicer or orca-flashforge)")
    slicer_version: Optional[str] = Field(None, description="Detected slicer version")
    platform: str = Field(..., description="Operating system (windows, darwin, linux)")
    files: List[FileEntry] = Field(default_factory=list, description="List of backed up files")
    total_files: int = Field(..., description="Total number of files in backup")
    total_size: int = Field(..., description="Total size of all files in bytes")
    compressed: bool = Field(default=True, description="Whether backup is compressed")

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}

    @property
    def size_mb(self) -> float:
        """Get total size in megabytes."""
        return self.total_size / (1024 * 1024)


class BackupInfo(BaseModel):
    """Information about a backup file."""

    backup_path: Path = Field(..., description="Path to backup file/directory")
    manifest: BackupManifest = Field(..., description="Backup manifest")
    is_valid: bool = Field(..., description="Whether backup passed verification")
    size_mb: float = Field(..., description="Backup size in megabytes")

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True
