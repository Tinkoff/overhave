from pathlib import Path

import click

from overhave.base_settings import OverhaveLoggingSettings
from overhave.cli.group import overhave
from overhave.transport import OverhaveS3Bucket, S3Manager, S3ManagerSettings


@overhave.group(short_help="Run s3 cloud interaction commands")
def s3() -> None:
    pass


@s3.group(short_help="S3 cloud bucket's interaction commands")
def bucket() -> None:
    pass


def _check_bucket_registered(name: str) -> None:
    if name in (item.value for item in list(OverhaveS3Bucket)):
        return
    click.secho(f"Note: specified s3 bucket name '{name}' not presented in OverhaveS3Bucket enum!", fg="yellow")


def _get_s3_manager() -> S3Manager:
    OverhaveLoggingSettings().setup_logging()
    manager = S3Manager(S3ManagerSettings(autocreate_buckets=False))
    manager.initialize()
    return manager


@bucket.command(short_help="Create s3 cloud bucket")
@click.option(
    "-n", "--name", type=str, help="Declared s3 bucket",
)
def create(name: str) -> None:
    """ Create s3 bucket. """
    _check_bucket_registered(name)
    _get_s3_manager().create_bucket(name)


@bucket.command(short_help="Delete s3 cloud bucket")
@click.option(
    "-n", "--name", type=str, help="Declared s3 bucket",
)
@click.option(
    "-f", "--force", is_flag=True, help="Delete all files in bucket, then delete bucket",
)
def delete(name: str, force: bool) -> None:
    """ Delete s3 bucket. """
    _check_bucket_registered(name)
    _get_s3_manager().delete_bucket(name, force=force)


@s3.command(short_help="Download file from s3 bucket")
@click.option(
    "-b", "--bucket", type=str, help="Declared s3 bucket",
)
@click.option(
    "-f", "--filename", type=str, help="Filename for downloading",
)
@click.option("-d", "--dir-to-save", type=str, help="Directory for saving file", default=".")
def download_file(bucket: str, filename: str, dir_to_save: str) -> None:
    """ Create s3 bucket. """
    _check_bucket_registered(bucket)
    _get_s3_manager().download_file(filename=filename, bucket=bucket, dir_to_save=Path(dir_to_save))
