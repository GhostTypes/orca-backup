"""Path utility functions."""

from datetime import datetime
from pathlib import Path


def ensure_directory(path: Path) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_backup_name(slicer_name: str, timestamp: datetime = None, compressed: bool = True) -> str:
    """Generate a backup filename with timestamp."""
    if timestamp is None:
        timestamp = datetime.now()

    timestamp_str = timestamp.strftime("%Y-%m-%d_%H-%M-%S")
    slicer_display = slicer_name.replace("-", "_").title()
    extension = ".zip" if compressed else ""

    return f"{slicer_display}_backup_{timestamp_str}{extension}"


def get_default_backup_dir() -> Path:
    """Get the default backup directory."""
    return Path.home() / "OrcaBackups"
