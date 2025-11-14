"""Backup restore functionality."""

import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from orca_backup.core.backup import create_backup
from orca_backup.core.detector import get_slicer_info
from orca_backup.core.verify import load_manifest, verify_backup
from orca_backup.models.slicer import SlicerInfo, SlicerType
from orca_backup.utils.compression import extract_archive


def get_restore_file_list(backup_path: Path) -> List[Tuple[Path, Path]]:
    """
    Get list of files to restore and their destinations.

    Args:
        backup_path: Path to backup

    Returns:
        List of (source, destination) tuples
    """
    manifest = load_manifest(backup_path)
    if not manifest:
        raise ValueError("Could not load backup manifest")

    # Determine slicer info
    slicer_type = SlicerType(manifest.slicer)
    slicer = get_slicer_info(slicer_type)

    file_list = []
    for file_entry in manifest.files:
        src = Path(file_entry.path)
        dst = slicer.config_path / file_entry.path
        file_list.append((src, dst))

    return file_list


def restore_backup(
    backup_path: Path,
    slicer_type: SlicerType = None,
    dry_run: bool = False,
    backup_existing: bool = True,
) -> bool:
    """
    Restore a backup to a slicer installation.

    Args:
        backup_path: Path to backup file/directory
        slicer_type: Target slicer type (auto-detected from backup if None)
        dry_run: If True, only show what would be restored
        backup_existing: If True, backup existing files before restore

    Returns:
        True if restore succeeded, False otherwise

    Raises:
        ValueError: If backup is invalid or slicer not found
        RuntimeError: If restore fails
    """
    # Verify backup
    if not verify_backup(backup_path, verbose=False):
        raise ValueError("Backup verification failed")

    # Load manifest to determine slicer type
    manifest = load_manifest(backup_path)
    if not manifest:
        raise ValueError("Could not load backup manifest")

    if slicer_type is None:
        slicer_type = SlicerType(manifest.slicer)

    slicer = get_slicer_info(slicer_type)
    if not slicer.exists:
        raise ValueError(f"{slicer.display_name} not found at {slicer.config_path}")

    # Get file list
    file_list = get_restore_file_list(backup_path)

    if dry_run:
        print(f"Would restore {len(file_list)} files to {slicer.config_path}")
        print("\nFiles to restore:")
        for src, dst in file_list[:10]:  # Show first 10
            print(f"  {src} -> {dst}")
        if len(file_list) > 10:
            print(f"  ... and {len(file_list) - 10} more files")
        return True

    # Backup existing configuration if requested
    if backup_existing and slicer.is_valid():
        print("Creating backup of existing configuration...")
        backup_dir = slicer.config_path.parent / "orca_backups_temp"
        backup_dir.mkdir(exist_ok=True)
        try:
            create_backup(slicer, backup_dir, compress=True, verify=False)
            print(f"Existing configuration backed up to {backup_dir}")
        except Exception as e:
            raise RuntimeError(f"Failed to backup existing configuration: {e}")

    # Extract backup to temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        if backup_path.is_file() and backup_path.suffix == ".zip":
            extract_archive(backup_path, temp_path)
            source_dir = temp_path
        else:
            source_dir = backup_path

        # Copy files to destination
        restored_count = 0
        for src_rel, dst in file_list:
            src = source_dir / src_rel
            if not src.exists():
                print(f"WARNING: File not found in backup: {src_rel}")
                continue

            # Create parent directory
            dst.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            try:
                shutil.copy2(src, dst)
                restored_count += 1
            except Exception as e:
                print(f"WARNING: Failed to restore {src_rel}: {e}")

    print(f"Restored {restored_count}/{len(file_list)} files")
    return restored_count == len(file_list)
