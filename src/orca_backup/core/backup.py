"""Backup creation functionality."""

import hashlib
import json
import platform
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from orca_backup.models.backup import BackupManifest, FileEntry
from orca_backup.models.slicer import SlicerInfo
from orca_backup.utils.compression import compress_directory
from orca_backup.utils.paths import ensure_directory, get_backup_name


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def copy_file_with_metadata(src: Path, dst: Path, base_path: Path) -> FileEntry:
    """
    Copy a file and create its metadata entry.

    Args:
        src: Source file path
        dst: Destination file path
        base_path: Base path for calculating relative paths

    Returns:
        FileEntry with file metadata
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

    relative_path = str(src.relative_to(base_path))
    size = src.stat().st_size
    checksum = calculate_sha256(src)

    return FileEntry(path=relative_path, size=size, sha256=checksum)


def create_backup_staging(slicer: SlicerInfo, staging_dir: Path) -> List[FileEntry]:
    """
    Create backup in a staging directory.

    Args:
        slicer: Slicer information
        staging_dir: Temporary staging directory

    Returns:
        List of file entries
    """
    file_entries: List[FileEntry] = []
    base_path = slicer.config_path

    # Copy main config file
    if slicer.conf_file:
        dst = staging_dir / slicer.conf_file.name
        entry = copy_file_with_metadata(slicer.conf_file, dst, base_path)
        file_entries.append(entry)

    # Copy entire user directory
    if slicer.user_dir:
        user_dst = staging_dir / "user"
        shutil.copytree(slicer.user_dir, user_dst, dirs_exist_ok=True)

        # Create entries for all files in user directory
        for file_path in slicer.user_dir.rglob("*"):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(base_path))
                size = file_path.stat().st_size
                checksum = calculate_sha256(file_path)
                file_entries.append(FileEntry(path=relative_path, size=size, sha256=checksum))

    # Copy custom_scripts if it exists
    if slicer.custom_scripts_dir and slicer.custom_scripts_dir.exists():
        scripts_dst = staging_dir / "custom_scripts"
        shutil.copytree(slicer.custom_scripts_dir, scripts_dst, dirs_exist_ok=True)

        for file_path in slicer.custom_scripts_dir.rglob("*"):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(base_path))
                size = file_path.stat().st_size
                checksum = calculate_sha256(file_path)
                file_entries.append(FileEntry(path=relative_path, size=size, sha256=checksum))

    return file_entries


def create_manifest(
    slicer: SlicerInfo, file_entries: List[FileEntry], compressed: bool
) -> BackupManifest:
    """Create backup manifest."""
    total_size = sum(entry.size for entry in file_entries)

    return BackupManifest(
        version="1.0",
        created_at=datetime.now(),
        slicer=slicer.name,  # Already a string due to use_enum_values
        slicer_version=slicer.version,
        platform=platform.system().lower(),
        files=file_entries,
        total_files=len(file_entries),
        total_size=total_size,
        compressed=compressed,
    )


def create_backup(
    slicer: SlicerInfo,
    output_dir: Path,
    compress: bool = True,
    verify: bool = True,
) -> Path:
    """
    Create a backup of a slicer configuration.

    Args:
        slicer: Slicer to backup
        output_dir: Directory to save backup
        compress: Whether to compress the backup (default: True)
        verify: Whether to verify the backup (default: True)

    Returns:
        Path to created backup file/directory

    Raises:
        ValueError: If slicer is invalid
        RuntimeError: If backup creation fails
    """
    if not slicer.is_valid():
        raise ValueError(f"Invalid slicer: {slicer.display_name} not properly installed")

    ensure_directory(output_dir)

    # Create temporary staging directory
    with tempfile.TemporaryDirectory() as temp_dir:
        staging_dir = Path(temp_dir) / "backup"
        staging_dir.mkdir()

        # Copy files to staging and collect metadata
        file_entries = create_backup_staging(slicer, staging_dir)

        # Create manifest
        manifest = create_manifest(slicer, file_entries, compress)

        # Write manifest to staging directory
        manifest_path = staging_dir / "backup_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest.model_dump(mode="json"), f, indent=2, default=str)

        # Generate output filename
        backup_name = get_backup_name(slicer.name, manifest.created_at, compress)  # name is already a string
        output_path = output_dir / backup_name

        if compress:
            # Compress to ZIP
            compress_directory(staging_dir, output_path)
        else:
            # Copy directory
            shutil.copytree(staging_dir, output_path)

    if verify:
        from orca_backup.core.verify import verify_backup

        if not verify_backup(output_path):
            raise RuntimeError("Backup verification failed")

    return output_path
