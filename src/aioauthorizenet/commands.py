"""Command line interface for simple POC Authorize.net API client."""

import asyncio
import json
import typing

import typer

from aioauthorizenet import client

APP = typer.Typer()


@APP.command()
def list_subscriptions(
    sub_ids: typing.List[str], identifier: str = typer.Option(...)
) -> None:
    """Display info about specified subscription ids.

    Args:
        identifier: name of client connection to use
        sub_ids: list of subscription IDs
    """
    auth = client.authentication(identifier)
    subscriptions = asyncio.run(client.get_subscriptions(auth, sub_ids))
    print(json.dumps(list(subscriptions), indent=2))


def run() -> None:
    """Command runner."""
    APP()
