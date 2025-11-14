# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

orca-backup is a cross-platform Python CLI tool for backing up and restoring OrcaSlicer and Orca-Flashforge slicer configurations. It uses Typer for CLI, Rich for terminal output, and Pydantic for data validation.

## Development Setup

Install in editable mode:
```bash
pip install -e .
```

Run the CLI during development:
```bash
orca-backup <command>
# or
python -m orca_backup <command>
```

## Code Architecture

### Module Structure

```
src/orca_backup/
├── cli.py              # Typer CLI commands (entry point)
├── core/               # Core business logic
│   ├── detector.py     # Slicer detection and path resolution
│   ├── backup.py       # Backup creation with manifest generation
│   ├── restore.py      # Restore with safety checks
│   └── verify.py       # Integrity verification (SHA256)
├── models/             # Pydantic data models
│   ├── slicer.py       # SlicerInfo, SlicerType enum
│   └── backup.py       # BackupManifest, FileEntry, BackupInfo
└── utils/              # Helper utilities
    ├── paths.py        # Path operations, backup naming
    └── compression.py  # ZIP operations
```

### Key Design Patterns

**Slicer Detection Flow:**
1. `detector.py` checks platform-specific paths (Windows AppData, macOS Library, Linux .config)
2. Supports Flatpak installations on Linux
3. Returns `SlicerInfo` objects with validation via Pydantic

**Backup Process:**
1. Create staging directory in temp
2. Copy `.conf` file and `user/` directory
3. Calculate SHA256 for each file → `FileEntry` list
4. Generate `BackupManifest` with metadata
5. Write manifest as `backup_manifest.json`
6. Compress to ZIP (optional)
7. Verify integrity if requested

**Restore Process:**
1. Verify backup integrity first
2. Auto-backup existing config to `orca_backups_temp/` (unless `--no-backup`)
3. Extract to temp directory
4. Copy files to slicer config path
5. Report success/warnings

### Critical Implementation Details

**Pydantic Configuration:**
- `SlicerInfo.name` uses `use_enum_values = True`, so it's already a string (not enum)
- Do NOT call `.value` on `slicer.name` - this was a bug that was fixed

**Platform Paths:**
```python
Windows: Path.home() / "AppData/Roaming/{OrcaSlicer|Orca-Flashforge}"
macOS:   Path.home() / "Library/Application Support/{OrcaSlicer|Orca-Flashforge}"
Linux:   Path.home() / ".config/{OrcaSlicer|Orca-Flashforge}"
Flatpak: Path.home() / ".var/app/io.github.softfever.OrcaSlicer/config/OrcaSlicer"
```

**What Gets Backed Up:**
- Main `.conf` file (includes recent files list, presets, settings)
- `user/` directory (custom filament/machine/process profiles)
- `custom_scripts/` directory (Orca-Flashforge only, if exists)

**What's Excluded:**
- System files (`system/`, `printers/`)
- Temporary data (`log/`, `ota/`, `*.conf.bak`)
- Auto-generated backups (`user_backup-*`)

### Unicode/Encoding Rules

**CRITICAL:** Windows console doesn't support Unicode emojis. Use plain ASCII text only:
- ✓ → "Yes" or remove entirely
- ✗ → "No" or "ERROR:"
- ❌ → "ERROR:"
- 🔍 → Remove or use "[cyan]...[/cyan]"
- ⚠ → "WARNING:"

Always test CLI output on Windows to catch encoding errors.

### Testing Commands

Test individual commands:
```bash
orca-backup list
orca-backup backup --slicer orcaslicer --output ./test_backups
orca-backup verify ./test_backups/Orcaslicer_backup_*.zip
orca-backup info ./test_backups/Orcaslicer_backup_*.zip
orca-backup restore ./test_backups/Orcaslicer_backup_*.zip --dry-run
```

## File Operations

All file operations use `pathlib.Path` for cross-platform compatibility. The `shutil` module handles directory copying with `copytree(..., dirs_exist_ok=True)`.

Backup manifest structure:
```json
{
  "version": "1.0",
  "created_at": "2025-11-13T20:51:12",
  "slicer": "orcaslicer",
  "slicer_version": "2.3.1-beta",
  "platform": "windows",
  "files": [
    {"path": "OrcaSlicer.conf", "size": 17400, "sha256": "abc123..."}
  ],
  "total_files": 44,
  "total_size": 40960,
  "compressed": true
}
```

## Common Modifications

**Adding a new CLI command:**
1. Add `@app.command()` decorated function in `cli.py`
2. Implement logic in appropriate `core/` module
3. Update README.md usage section

**Supporting a new slicer:**
1. Add enum value to `SlicerType` in `models/slicer.py`
2. Update path mappings in `detector.get_slicer_paths()`
3. Add display name to `get_slicer_info()`

**Changing backup contents:**
- Modify `backup.create_backup_staging()` to include/exclude files
- Update README.md "What Gets Backed Up" section
