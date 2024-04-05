import json

from myaakash import SessionService

from aakashdm.utils import get_token_file

TOKEN_PATH = get_token_file()


def get_sessions() -> dict:
    try:
        with open(TOKEN_PATH) as f:
            sessions = json.load(f)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        sessions = {}

    return sessions


def get_session(psid: str) -> dict:
    sessions = get_sessions()
    session = sessions.get(psid)

    if session:
        return session

    return {}


def save_session(myaakash: SessionService) -> bool:
    if not myaakash.logged_in:
        return False

    name = myaakash.profile["name"]
    psid = myaakash.profile["psid"]

    session = {
        "name": name,
        "PSID": psid,
        "tokens": myaakash.tokens,
    }

    sessions = get_sessions()
    sessions[psid] = session
    with open(TOKEN_PATH, "w+") as f:
        json.dump(sessions, f)

    return True


def remove_session(psid: str) -> bool:
    sessions = get_sessions()

    if psid in sessions.keys():
        sessions.pop(psid)
        with open(TOKEN_PATH, "w+") as f:
            json.dump(sessions, f)
        return True

    return False
