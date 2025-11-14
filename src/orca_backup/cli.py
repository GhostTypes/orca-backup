"""CLI interface for orca-backup."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from orca_backup.core.backup import create_backup
from orca_backup.core.detector import detect_slicers, get_installed_slicers, get_slicer_info
from orca_backup.core.restore import restore_backup
from orca_backup.core.verify import get_backup_info, verify_backup
from orca_backup.models.slicer import SlicerType
from orca_backup.utils.paths import get_default_backup_dir

app = typer.Typer(
    name="orca-backup",
    help="Backup and restore tool for OrcaSlicer and Orca-Flashforge configurations",
    add_completion=False,
)
console = Console()


@app.command()
def list():
    """List detected slicer installations."""
    slicers = detect_slicers()

    table = Table(title="Detected Slicers", show_header=True, header_style="bold magenta")
    table.add_column("Slicer", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Version", style="yellow")
    table.add_column("Location", style="blue")

    for slicer in slicers:
        status = "Installed" if slicer.is_valid() else "Not found"
        status_style = "green" if slicer.is_valid() else "red"
        version = slicer.version or "Unknown"
        location = str(slicer.config_path)

        table.add_row(slicer.display_name, f"[{status_style}]{status}[/]", version, location)

    console.print(table)

    installed_count = sum(1 for s in slicers if s.is_valid())
    console.print(f"\n[bold]Found {installed_count}/{len(slicers)} installed slicers[/bold]")


@app.command()
def backup(
    slicer: str = typer.Option(
        "all",
        "--slicer",
        "-s",
        help="Slicer to backup (orcaslicer, orca-flashforge, or all)",
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output directory for backups"
    ),
    compress: bool = typer.Option(True, "--compress/--no-compress", help="Compress backup to ZIP"),
    verify: bool = typer.Option(
        True, "--verify/--no-verify", help="Verify backup after creation"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Create a backup of slicer configuration(s)."""
    output_dir = output or get_default_backup_dir()
    output_dir = Path(output_dir)

    # Determine which slicers to backup
    if slicer.lower() == "all":
        slicers_to_backup = get_installed_slicers()
        if not slicers_to_backup:
            console.print("[red]ERROR: No installed slicers found[/red]")
            raise typer.Exit(1)
    else:
        try:
            slicer_type = SlicerType(slicer.lower())
            slicer_info = get_slicer_info(slicer_type)
            if not slicer_info.is_valid():
                console.print(f"[red]ERROR: {slicer_info.display_name} not found[/red]")
                raise typer.Exit(1)
            slicers_to_backup = [slicer_info]
        except ValueError:
            console.print(f"[red]ERROR: Invalid slicer: {slicer}[/red]")
            console.print("Valid options: orcaslicer, orca-flashforge, all")
            raise typer.Exit(1)

    # Create backups
    for slicer_info in slicers_to_backup:
        console.print(f"\n[cyan]Backing up {slicer_info.display_name}...[/cyan]")
        if verbose:
            console.print(f"   Location: {slicer_info.config_path}")
            console.print(f"   Version: {slicer_info.version or 'Unknown'}")

        try:
            backup_path = create_backup(
                slicer_info, output_dir, compress=compress, verify=verify
            )
            console.print(f"[green]Backup created successfully![/green]")
            console.print(f"   Location: {backup_path}")

            if backup_path.is_file():
                size_mb = backup_path.stat().st_size / (1024 * 1024)
                console.print(f"   Size: {size_mb:.2f} MB")
        except Exception as e:
            console.print(f"[red]ERROR: Backup failed: {e}[/red]")
            if verbose:
                import traceback

                console.print(traceback.format_exc())
            raise typer.Exit(1)


@app.command()
def restore(
    backup_path: Path = typer.Argument(..., help="Path to backup file or directory"),
    slicer: Optional[str] = typer.Option(
        None, "--slicer", "-s", help="Target slicer (auto-detected if not specified)"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be restored"),
    backup_existing: bool = typer.Option(
        True, "--backup-existing/--no-backup", help="Backup existing files before restore"
    ),
):
    """Restore a backup to a slicer installation."""
    if not backup_path.exists():
        console.print(f"[red]ERROR: Backup not found: {backup_path}[/red]")
        raise typer.Exit(1)

    # Determine slicer type
    slicer_type = None
    if slicer:
        try:
            slicer_type = SlicerType(slicer.lower())
        except ValueError:
            console.print(f"[red]ERROR: Invalid slicer: {slicer}[/red]")
            raise typer.Exit(1)

    console.print(f"[cyan]Loading backup from {backup_path}...[/cyan]")

    try:
        success = restore_backup(
            backup_path,
            slicer_type=slicer_type,
            dry_run=dry_run,
            backup_existing=backup_existing,
        )

        if dry_run:
            console.print("\n[yellow]This was a dry run. No files were changed.[/yellow]")
        elif success:
            console.print("\n[green]Restore completed successfully![/green]")
        else:
            console.print("\n[yellow]WARNING: Restore completed with warnings[/yellow]")

    except Exception as e:
        console.print(f"[red]ERROR: Restore failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def verify(backup_path: Path = typer.Argument(..., help="Path to backup file or directory")):
    """Verify the integrity of a backup."""
    if not backup_path.exists():
        console.print(f"[red]ERROR: Backup not found: {backup_path}[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]Verifying backup: {backup_path}[/cyan]")

    is_valid = verify_backup(backup_path, verbose=True)

    if is_valid:
        console.print("\n[green]Backup verification passed![/green]")
    else:
        console.print("\n[red]ERROR: Backup verification failed![/red]")
        raise typer.Exit(1)


@app.command()
def info(backup_path: Path = typer.Argument(..., help="Path to backup file or directory")):
    """Show information about a backup."""
    if not backup_path.exists():
        console.print(f"[red]ERROR: Backup not found: {backup_path}[/red]")
        raise typer.Exit(1)

    backup_info = get_backup_info(backup_path)
    if not backup_info:
        console.print("[red]ERROR: Could not load backup information[/red]")
        raise typer.Exit(1)

    manifest = backup_info.manifest

    table = Table(title="Backup Information", show_header=False, box=None)
    table.add_column("Field", style="cyan bold")
    table.add_column("Value", style="white")

    table.add_row("Slicer", manifest.slicer.title())
    table.add_row("Version", manifest.slicer_version or "Unknown")
    table.add_row("Created", manifest.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    table.add_row("Platform", manifest.platform.title())
    table.add_row("Total Files", str(manifest.total_files))
    table.add_row("Total Size", f"{manifest.size_mb:.2f} MB")
    table.add_row("Backup Size", f"{backup_info.size_mb:.2f} MB")
    table.add_row("Compressed", "Yes" if manifest.compressed else "No")
    table.add_row("Valid", "Yes" if backup_info.is_valid else "No")

    console.print(table)


@app.command()
def version():
    """Show version information."""
    from orca_backup import __version__

    console.print(f"orca-backup version {__version__}")


if __name__ == "__main__":
    app()
