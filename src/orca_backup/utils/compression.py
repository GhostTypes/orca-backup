"""Compression and archiving utilities."""

import zipfile
from pathlib import Path
from typing import List


def compress_directory(source_dir: Path, output_file: Path, exclude_patterns: List[str] = None) -> Path:
    """
    Compress a directory to a ZIP file.

    Args:
        source_dir: Directory to compress
        output_file: Output ZIP file path
        exclude_patterns: List of patterns to exclude (not implemented yet)

    Returns:
        Path to created ZIP file
    """
    if exclude_patterns is None:
        exclude_patterns = []

    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in source_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(source_dir)
                zipf.write(file_path, arcname)

    return output_file


def extract_archive(archive_path: Path, output_dir: Path) -> Path:
    """
    Extract a ZIP archive to a directory.

    Args:
        archive_path: Path to ZIP file
        output_dir: Directory to extract to

    Returns:
        Path to extraction directory
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(archive_path, "r") as zipf:
        zipf.extractall(output_dir)

    return output_dir


def is_valid_zip(archive_path: Path) -> bool:
    """Check if a file is a valid ZIP archive."""
    try:
        with zipfile.ZipFile(archive_path, "r") as zipf:
            return zipf.testzip() is None
    except (zipfile.BadZipFile, FileNotFoundError):
        return False
