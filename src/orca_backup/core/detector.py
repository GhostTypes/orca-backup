"""Slicer detection functionality."""

import json
import platform
import re
from pathlib import Path
from typing import Dict, List, Optional

from orca_backup.models.slicer import SlicerInfo, SlicerType


def get_slicer_paths() -> Dict[str, Dict[str, Path]]:
    """Get platform-specific slicer config directory paths."""
    system = platform.system().lower()

    if system == "windows":
        base = Path.home() / "AppData" / "Roaming"
        return {
            "orcaslicer": base / "OrcaSlicer",
            "orca-flashforge": base / "Orca-Flashforge",
        }
    elif system == "darwin":  # macOS
        base = Path.home() / "Library" / "Application Support"
        return {
            "orcaslicer": base / "OrcaSlicer",
            "orca-flashforge": base / "Orca-Flashforge",
        }
    elif system == "linux":
        # Check for Flatpak first
        flatpak_path = (
            Path.home()
            / ".var"
            / "app"
            / "io.github.softfever.OrcaSlicer"
            / "config"
            / "OrcaSlicer"
        )
        if flatpak_path.exists():
            return {
                "orcaslicer": flatpak_path,
                "orca-flashforge": Path.home() / ".config" / "Orca-Flashforge",
            }
        # Standard Linux paths
        base = Path.home() / ".config"
        return {
            "orcaslicer": base / "OrcaSlicer",
            "orca-flashforge": base / "Orca-Flashforge",
        }
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


def extract_version(conf_file: Path) -> Optional[str]:
    """Extract slicer version from config file."""
    try:
        with open(conf_file, "r", encoding="utf-8") as f:
            content = f.read()
            # Try to parse as JSON
            if content.strip().startswith("{"):
                data = json.loads(content.split("# MD5")[0])  # Remove checksum line
                if "header" in data:
                    # Extract version from header like "OrcaSlicer 2.3.1-beta"
                    match = re.search(r"(\d+\.\d+\.\d+(?:-\w+)?)", data["header"])
                    if match:
                        return match.group(1)
                if "app" in data and "version" in data["app"]:
                    return data["app"]["version"]
    except Exception:
        pass
    return None


def get_slicer_info(slicer_type: SlicerType) -> SlicerInfo:
    """Get information about a specific slicer installation."""
    paths = get_slicer_paths()
    config_path = paths[slicer_type.value]

    display_names = {
        SlicerType.ORCASLICER: "OrcaSlicer",
        SlicerType.ORCA_FLASHFORGE: "Orca-Flashforge",
    }

    conf_filenames = {
        SlicerType.ORCASLICER: "OrcaSlicer.conf",
        SlicerType.ORCA_FLASHFORGE: "Orca-Flashforge.conf",
    }

    exists = config_path.exists()
    conf_file = config_path / conf_filenames[slicer_type] if exists else None
    user_dir = config_path / "user" if exists else None
    custom_scripts_dir = config_path / "custom_scripts" if exists else None

    # Only include custom_scripts if it actually exists
    if custom_scripts_dir and not custom_scripts_dir.exists():
        custom_scripts_dir = None

    version = None
    if conf_file and conf_file.exists():
        version = extract_version(conf_file)

    return SlicerInfo(
        name=slicer_type,
        display_name=display_names[slicer_type],
        config_path=config_path,
        exists=exists,
        version=version,
        conf_file=conf_file if conf_file and conf_file.exists() else None,
        user_dir=user_dir if user_dir and user_dir.exists() else None,
        custom_scripts_dir=custom_scripts_dir,
    )


def detect_slicers() -> List[SlicerInfo]:
    """Detect all installed slicers."""
    return [
        get_slicer_info(SlicerType.ORCASLICER),
        get_slicer_info(SlicerType.ORCA_FLASHFORGE),
    ]


def get_installed_slicers() -> List[SlicerInfo]:
    """Get only installed and valid slicers."""
    return [slicer for slicer in detect_slicers() if slicer.is_valid()]
