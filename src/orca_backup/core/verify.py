"""Backup verification functionality."""

import hashlib
import json
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Tuple

from orca_backup.models.backup import BackupInfo, BackupManifest
from orca_backup.utils.compression import extract_archive, is_valid_zip


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def load_manifest(backup_path: Path) -> Optional[BackupManifest]:
    """Load backup manifest from a backup file or directory."""
    try:
        if backup_path.is_file() and backup_path.suffix == ".zip":
            # Extract manifest from ZIP
            with zipfile.ZipFile(backup_path, "r") as zipf:
                with zipf.open("backup_manifest.json") as f:
                    data = json.load(f)
                    return BackupManifest(**data)
        elif backup_path.is_dir():
            # Load manifest from directory
            manifest_path = backup_path / "backup_manifest.json"
            if manifest_path.exists():
                with open(manifest_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return BackupManifest(**data)
    except Exception:
        return None

    return None


def verify_backup(backup_path: Path, verbose: bool = False) -> bool:
    """
    Verify the integrity of a backup.

    Args:
        backup_path: Path to backup file or directory
        verbose: Whether to print detailed verification info

    Returns:
        True if backup is valid, False otherwise
    """
    if not backup_path.exists():
        if verbose:
            print(f"ERROR: Backup not found: {backup_path}")
        return False

    # Check if it's a valid ZIP
    is_compressed = backup_path.is_file() and backup_path.suffix == ".zip"
    if is_compressed:
        if not is_valid_zip(backup_path):
            if verbose:
                print("ERROR: Invalid or corrupted ZIP file")
            return False
        if verbose:
            print("Backup file is valid ZIP archive")

    # Load and verify manifest
    manifest = load_manifest(backup_path)
    if not manifest:
        if verbose:
            print("ERROR: Manifest file not found or invalid")
        return False

    if verbose:
        print("Manifest file found and valid")

    # Verify files and checksums
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        if is_compressed:
            # Extract to temp directory
            extract_archive(backup_path, temp_path)
            check_dir = temp_path
        else:
            check_dir = backup_path

        # Verify all files exist and checksums match
        missing_files = []
        checksum_mismatches = []

        for file_entry in manifest.files:
            file_path = check_dir / file_entry.path
            if not file_path.exists():
                missing_files.append(file_entry.path)
                continue

            actual_checksum = calculate_sha256(file_path)
            if actual_checksum != file_entry.sha256:
                checksum_mismatches.append(file_entry.path)

        if missing_files:
            if verbose:
                print(f"ERROR: Missing files: {len(missing_files)}")
                for f in missing_files[:5]:  # Show first 5
                    print(f"  - {f}")
            return False

        if checksum_mismatches:
            if verbose:
                print(f"ERROR: Checksum mismatches: {len(checksum_mismatches)}")
                for f in checksum_mismatches[:5]:  # Show first 5
                    print(f"  - {f}")
            return False

        if verbose:
            print(f"All {manifest.total_files} files present")
            print("All checksums verified")
            print("Backup is valid and complete")

    return True


def get_backup_info(backup_path: Path) -> Optional[BackupInfo]:
    """Get information about a backup."""
    manifest = load_manifest(backup_path)
    if not manifest:
        return None

    is_valid = verify_backup(backup_path, verbose=False)

    if backup_path.is_file():
        size_mb = backup_path.stat().st_size / (1024 * 1024)
    else:
        total_size = sum(f.stat().st_size for f in backup_path.rglob("*") if f.is_file())
        size_mb = total_size / (1024 * 1024)

    return BackupInfo(
        backup_path=backup_path, manifest=manifest, is_valid=is_valid, size_mb=size_mb
    )
