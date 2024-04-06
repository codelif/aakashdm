import click
from myaakash import SessionService

import aakashdm.sessionizer


@click.group("sessions")
def sessions():
    """Manage MyAakash Sessions"""


@sessions.command("list")
def list_sessions():
    sessions = aakashdm.sessionizer.get_sessions()

    for index, session in enumerate(sessions.values(), start=1):
        name = session["name"]
        timestamp = session["tokens"]["login_timestamp"]
        psid = session["PSID"]

        click.echo(f"Session #{index}")
        click.echo(f" - PSID: {psid}")
        click.echo(f" - NAME: {name}")
        click.echo(f" - LOGON: {timestamp}\n")

    if not sessions:
        click.echo("Please add a session first!")


@sessions.command("add")
@click.argument("psid", required=True, type=str)
@click.password_option(
    type=str, confirmation_prompt=False, help="If not passed, a prompt is given."
)
def add_session(psid: str, password: str):
    session = aakashdm.sessionizer.get_session(psid)

    if session:
        confirm = input(
            "A session already exists with PSID '%s'.\nDo you want to replace this session? [y|n] "
            % psid
        )
        if confirm != "y":
            click.echo("Session creation aborted!")
            return
        aakash = SessionService()
        aakash.token_login(session["tokens"])
        aakash.logout()
        del aakash

    aakash = SessionService()
    aakash.login(psid, password)
    aakashdm.sessionizer.save_session(aakash)
    click.echo("Session with PSID '%s' successfully created." % psid)


def sessions_shell_completion(ctx, params, incomplete):
    sessions = aakashdm.sessionizer.get_sessions()
    if not incomplete:
        return list(sessions.keys())

    return [k for k in sessions.keys() if k.startswith(incomplete)]


@sessions.command("remove")
@click.argument("psid", shell_complete=sessions_shell_completion)
def remove_session(psid: str):
    removed = aakashdm.sessionizer.remove_session(psid)

    if not removed:
        click.echo("Session with PSID '%s' does not exist." % psid)
    else:
        click.echo("Session with PSID '%s' has been removed." % psid)
