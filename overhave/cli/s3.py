import click

from overhave.base_settings import OverhaveLoggingSettings
from overhave.cli.group import overhave
from overhave.transport import OverhaveS3Bucket, S3Manager, S3ManagerSettings


@overhave.group(short_help="Run Overhave s3 cloud interaction commands")
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
    "-n", "--name", type=str, help="Overhave declared s3 bucket",
)
def create(name: str) -> None:
    """ Create s3 bucket. """
    _check_bucket_registered(name)
    _get_s3_manager().create_bucket(name)


@bucket.command(short_help="Delete s3 cloud bucket")
@click.option(
    "-n", "--name", type=str, help="Overhave declared s3 bucket",
)
@click.option(
    "-f", "--force", is_flag=True, help="Delete all files in bucket, then delete bucket",
)
def delete(name: str, force: bool) -> None:
    """ Delete s3 bucket. """
    _check_bucket_registered(name)
    _get_s3_manager().delete_bucket(name, force=force)
