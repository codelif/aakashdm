import os
import platform
from aakashdm import PROG, TOKEN_FILE


def get_user_data_folder(make_folder: bool = True) -> str:
    """Returns OS-specific application user data storage folder. Makes the directory if not present.

    Returns:
        str: user data storage folder
    """
    system = platform.system().lower()

    if system == "darwin":
        user_data = os.path.expanduser("~/Library/Application Support")
    elif system == "linux":
        user_data = os.environ.get("XDG_DATA_HOME")
        if not user_data:
            user_data = os.path.expanduser("~/.local/share")
    elif system == "windows":
        user_data = os.environ["APPDATA"]

    user_data = os.path.join(user_data, PROG)
    if make_folder:
        os.makedirs(user_data, exist_ok=True)

    return user_data


def get_token_file() -> str:
    """Returns path of token file while being OS aware.

    Returns:
        str: token file path
    """
    return os.path.join(get_user_data_folder(), TOKEN_FILE)
