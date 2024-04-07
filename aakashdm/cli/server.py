import click

from aakashdm.server import server as flask_server


@click.group("server")
def server():
    "AakashDM Server Utilities"


@server.command("run")
@click.option("--debug", is_flag=True, type=bool, help="Start server in debug mode")
@click.option(
    "--host", type=str, help="Server host", default="127.0.0.1", show_default=True
)
@click.option("--port", type=int, help="Server port", default=8000, show_default=True)
def run_server(debug: bool, host: str, port: int):
    flask_server.static_folder

    flask_server.run(host, port, debug)
