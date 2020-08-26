"""Manage Authorize.net Transaction Key."""

import contextlib
import getpass
import json
import pathlib
import tempfile
import time

KEY_DIR = pathlib.Path(tempfile.gettempdir(), "aioauthorizenet")
KEY_FILE = KEY_DIR / "key.txt"


def destroy(file_path: pathlib.Path) -> None:
    """Zero fill and delete key file.

    Args:
        file_path: path to key file
    """
    with contextlib.suppress(FileNotFoundError):
        with file_path.open("wb") as handle:
            handle.seek(100)
            handle.write(b"\0")
        file_path.unlink(True)


def destroy_all() -> None:
    """Destroy all session files found."""
    for key_path in list_all():
        destroy(key_path)


def get_file_path(identifier: str) -> pathlib.Path:
    """Get path to key file for this identifier.

    Args:
        identifier: name for this client connection

    Returns:
        Path to file
    """
    return KEY_DIR / f"{identifier}.key"


def list_all():
    """List all key files.

    Returns:
        List of file paths
    """
    return KEY_DIR.glob("*.key")


def obtain(identifier: str) -> tuple:
    """Get login ID and key from file or prompt.

    Args:
        identifier: name for this client connection

    Returns:
        Tuple of API Login ID and Transaction Key
    """
    try:
        login_id, key = read(identifier)
    except FileNotFoundError:
        login_id, key = prompt(identifier)
        write(identifier, login_id, key)

    return login_id, key


def prompt(identifier) -> tuple:
    """Credential entry helper.

    Returns:
        Tuple of login_id, key
    """
    login_id = input(f"API Login ID for {identifier}: ")
    key = getpass.getpass(f"API Transaction Key for {identifier}: ")
    return (login_id, key)


def read(identifier: str) -> tuple:
    """Get API Login ID and Transaction Key.

    Args:
        identifier: name for this client connection

    Returns:
        API Login ID and Transaction Key
    """
    with get_file_path(identifier).open() as handle:
        login_id, key = json.load(handle)
    return (login_id, key)


def write(identifier: str, login_id: str, key: str) -> None:
    """Create/update API key file with API key.

    Args:
        identifier: what to call this client connection
        login_id: Authorize.net API Login ID
        key: the API Transaction Key to be recorded
    """
    KEY_DIR.mkdir(exist_ok=True)
    KEY_DIR.chmod(0o700)
    key_file = get_file_path(identifier)
    key_file.touch(mode=0o600, exist_ok=True)
    with key_file.open("w") as handle:
        json.dump([login_id, key], handle)
