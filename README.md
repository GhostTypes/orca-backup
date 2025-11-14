# orca-backup

A cross-platform command-line tool for backing up and restoring OrcaSlicer and Orca-Flashforge configurations.

## Features

- Automatic detection of installed slicers (OrcaSlicer and Orca-Flashforge)
- Complete backup of user profiles, configurations, and custom settings
- Compressed ZIP backups with integrity verification
- Cross-platform support (Windows, macOS, Linux)
- Restore functionality with safety checks
- Backup verification and information display
- No system files or temporary data included in backups

## Installation

```bash
pip install orca-backup
```

Or install from source:

```bash
git clone https://github.com/yourusername/orca-backup-tool.git
cd orca-backup-tool
pip install -e .
```

## Usage

### List detected slicers

```bash
orca-backup list
```

Shows all installed slicers and their versions.

### Create a backup

Backup a specific slicer:

```bash
orca-backup backup --slicer orcaslicer
orca-backup backup --slicer orca-flashforge
```

Backup all installed slicers:

```bash
orca-backup backup --slicer all
```

Specify custom output directory:

```bash
orca-backup backup --slicer orcaslicer --output /path/to/backups
```

Create uncompressed backup:

```bash
orca-backup backup --slicer orcaslicer --no-compress
```

Skip verification:

```bash
orca-backup backup --slicer orcaslicer --no-verify
```

### Restore a backup

```bash
orca-backup restore /path/to/backup.zip
```

Dry run (show what would be restored without making changes):

```bash
orca-backup restore /path/to/backup.zip --dry-run
```

Restore without backing up existing files first:

```bash
orca-backup restore /path/to/backup.zip --no-backup
```

### Verify backup integrity

```bash
orca-backup verify /path/to/backup.zip
```

Checks that the backup is valid and all files are intact.

### Show backup information

```bash
orca-backup info /path/to/backup.zip
```

Displays detailed information about a backup including slicer version, file count, size, and validity.

### Display version

```bash
orca-backup version
```

## What Gets Backed Up

The tool backs up only essential user data:

- Main configuration file (OrcaSlicer.conf / Orca-Flashforge.conf)
- User profiles directory (user/)
  - Custom filament profiles
  - Custom machine configurations
  - Custom process settings
- Custom scripts (if present in Orca-Flashforge)

System files, vendor presets, temporary files, and logs are excluded from backups.

## Default Backup Location

Backups are saved to `~/OrcaBackups` by default. Use the `--output` option to specify a different location.

## Backup Naming

Backups are automatically named with timestamps:

```
Orcaslicer_backup_2025-11-13_20-51-12.zip
Orca_Flashforge_backup_2025-11-13_20-54-24.zip
```

## Automated Backups

To run automated backups, use your system's scheduler:

**Windows (Task Scheduler):**
```
schtasks /create /tn "OrcaSlicer Backup" /tr "orca-backup backup --slicer all" /sc weekly
```

**Linux/macOS (cron):**
```
0 0 * * 0 orca-backup backup --slicer all
```

## Requirements

- Python 3.9 or higher
- Windows, macOS, or Linux
