from datetime import timedelta
from pathlib import Path

import typer

from overhave.base_settings import LoggingSettings
from overhave.transport import OverhaveS3Bucket, OverhaveS3ManagerSettings, S3Manager
from overhave.utils import get_current_time

s3_app = typer.Typer(short_help="Run s3 cloud interaction commands")

s3_bucket_app = typer.Typer(short_help="S3 cloud bucket's interaction commands")
s3_app.add_typer(s3_bucket_app, name="bucket")


def _check_bucket_registered(name: str) -> None:
    if name in (item.value for item in list(OverhaveS3Bucket)):
        return
    typer.secho(f"Note: specified s3 bucket name '{name}' not presented in OverhaveS3Bucket enum!", fg="yellow")


def _get_s3_manager() -> S3Manager:
    LoggingSettings().setup_logging()
    manager = S3Manager(OverhaveS3ManagerSettings(autocreate_buckets=False))
    manager.initialize()
    return manager


@s3_bucket_app.command(short_help="Create s3 cloud bucket")
def create(name: str = typer.Option(..., "-n", "--name", help="Declared s3 bucket")) -> None:
    """Create s3 bucket."""
    _check_bucket_registered(name)
    _get_s3_manager().create_bucket(name)


@s3_bucket_app.command(short_help="Delete s3 cloud bucket")
def delete(
    name: str = typer.Option(..., "-n", "--name", help="Declared s3 bucket"),
    force: bool = typer.Option(
        False, "-f", "--force", is_flag=True, help="Delete all files in bucket, then delete bucket"
    ),
) -> None:
    """Delete s3 bucket."""
    _check_bucket_registered(name)
    _get_s3_manager().delete_bucket(name, force=force)


@s3_bucket_app.command(short_help="Remove old s3 cloud bucket files")
def remove_files(
    name: str = typer.Option(..., "-n", "--name", help="Declared s3 bucket"),
    days: int = typer.Option(..., "-d", "--days", help="Remove all files in bucket older then specified days value"),
) -> None:
    """Remove s3 bucket files older than specified number of days."""
    _check_bucket_registered(name)
    manager = _get_s3_manager()
    target_date = get_current_time() - timedelta(days=days)

    objects = manager.get_bucket_objects(name)
    objects_to_delete = []
    for obj in objects:
        if not obj.modified_at < target_date:
            continue
        objects_to_delete.append(obj)
    if not objects_to_delete:
        typer.secho(f"No one object older than {days} days.")
        return
    typer.secho(f"Objects older then {days} days: {[x.name for x in objects_to_delete]}")
    manager.delete_bucket_objects(bucket=name, objects=objects_to_delete)


@s3_app.command(short_help="Download file from s3 bucket")
def download_file(
    bucket: str = typer.Option(..., "-b", "--bucket", help="Declared s3 bucket"),
    filename: str = typer.Option(..., "-f", "--filename", help="Filename for downloading"),
    dir_to_save: str = typer.Option(".", help="Directory for saving file"),
) -> None:
    """Create s3 bucket."""
    _check_bucket_registered(bucket)
    _get_s3_manager().download_file(filename=filename, bucket=bucket, dir_to_save=Path(dir_to_save))
