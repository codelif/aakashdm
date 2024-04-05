import click

from aakashdm import PROG, __version__
from aakashdm.cli.downloader import download
from aakashdm.cli.sessions import sessions


@click.group(PROG)
@click.version_option(__version__, "--version", "-v")
@click.help_option("--help", "-h")
def cli():
    """MyAakash Download Manager"""


cli.add_command(sessions)
cli.add_command(download)
