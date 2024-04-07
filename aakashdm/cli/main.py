import click

from aakashdm import PROG, __version__
from aakashdm.cli.downloader import targets
from aakashdm.cli.server import server
from aakashdm.cli.sessions import sessions
from aakashdm.cli.tests import tests


@click.group(PROG)
@click.version_option(__version__, "--version", "-v")
@click.help_option("--help", "-h")
def cli():
    """MyAakash Download Manager"""


cli.add_command(sessions)
cli.add_command(targets)
cli.add_command(tests)
cli.add_command(server)
