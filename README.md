<div align="center">
  <h1>orca-backup</h1>
  <img src="https://img.shields.io/badge/Python-3.9%2B-yellow?style=for-the-badge&logo=python">
  <p>A cross-platform command-line tool for backing up and restoring OrcaSlicer and Orca-FlashForge configurations.</p>
</div>


<br>

<div align="center">
  <h2>Features</h2>
</div>

<div align="center">
<table>
  <tr>
    <th>Feature</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>Automatic Detection</td>
    <td>Identifies installed slicers (OrcaSlicer, Orca-FlashForge)</td>
  </tr>
  <tr>
    <td>Full Configuration Backup</td>
    <td>User profiles, config files, scripts, and custom settings</td>
  </tr>
  <tr>
    <td>ZIP Compression</td>
    <td>Integrity-checked compressed backups</td>
  </tr>
  <tr>
    <td>Cross-Platform</td>
    <td>Works on Windows, macOS, and Linux</td>
  </tr>
  <tr>
    <td>Safe Restore</td>
    <td>Includes pre-restore safety checks and optional dry-run</td>
  </tr>
  <tr>
    <td>Backup Verification</td>
    <td>Ensures backup integrity and displays backup details</td>
  </tr>
  <tr>
    <td>No Junk Files</td>
    <td>Excludes system files, presets, logs, and temporary data</td>
  </tr>
</table>
</div>

<br>

<div align="center">
  <h2>Installation</h2>
</div>

<div align="center">

```bash
pip install orca-backup
git clone https://github.com/GhostTypes/orca-backup-tool.git
cd orca-backup-tool
pip install -e .
```
</div> 
<br> 
<div align="center"> 
  <h2>Usage</h2> 
</div>


<div align="center"> 
  <h3>List detected slicers</h3> 

  ```
  orca-backup list
  ```
</div>

<br>

<div align="center">
  <h3>Create a Backup</h3>

  ```bash
# General Usage
orca-backup backup --slicer orcaslicer
orca-backup backup --slicer orca-flashforge
orca-backup backup --slicer all

# Specify custom output directory
orca-backup backup --slicer orcaslicer --output /path/to/backups

# Create uncompressed backup
orca-backup backup --slicer orcaslicer --no-compress

# Skip verification
orca-backup backup --slicer orcaslicer --no-verify
```
  
</div>

<div align="center">
  <h3>Restore a Backup</h3>

  ```bash
orca-backup restore /path/to/backup.zip

# Dry run (show actions without applying changes)
orca-backup restore /path/to/backup.zip --dry-run

# Restore without automatically backing up existing files
orca-backup restore /path/to/backup.zip --no-backup
```
  
</div>

<div align="center">
  <h3>Verify or Inspect Backups</h3>

```bash

# Verify backup integrity
orca-backup verify /path/to/backup.zip

# Display detailed backup information
orca-backup info /path/to/backup.zip
```
  
</div>



<div align="center">
  <h2>What Gets Backed Up</h2>
</div>

<div align="center">
<table>
<tr>
  <th>Category</th>
  <th>Included</th>
</tr>

<tr>
  <td>Main Configuration</td>
  <td>OrcaSlicer.conf / Orca-FlashForge.conf</td>
</tr>

<tr>
  <td>User Profiles</td>
  <td>
    Filament profiles<br>
    Machine configurations<br>
    Process settings
  </td>
</tr>

<tr>
  <td>Custom Scripts</td>
  <td>Orca-FlashForge user scripts (if present)</td>
</tr>

<tr>
  <td>Excluded</td>
  <td>System files, vendor presets, logs, temporary files</td>
</tr>
</table>
</div>


<br>

<div align="center">
  <h2>Default Backup Location</h2>
  <p>
    Backups are stored inside a folder named <code>OrcaBackups</code> located in your user’s home directory.<br>
    This directory is automatically created if it does not exist.
  </p>
</div>

<div align="center">
<table>
<tr>
  <th>Operating System</th>
  <th>Default Backup Path</th>
</tr>

<tr>
  <td>Windows</td>
  <td><code>C:\Users\<your-username>\OrcaBackups</code></td>
</tr>

<tr>
  <td>macOS</td>
  <td><code>/Users/<your-username>/OrcaBackups</code></td>
</tr>

<tr>
  <td>Linux</td>
  <td><code>/home/<your-username>/OrcaBackups</code></td>
</tr>
</table>
</div>

<br>

<div align="center">
  <p>
    Use the <code>--output</code> option if you want to store backups in a different directory.
  </p>
</div>
