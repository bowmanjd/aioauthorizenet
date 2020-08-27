"""Simple POC Authorize.net API client."""

import asyncio
import typing

import httpx

from aioauthorizenet import key


def authentication(identifier: str) -> dict:
    """Get, cache, and return auth json for Authorize.net calls.

    Args:
        identifier: name for this client connection

    Returns:
        Authorize.net merchantAuthentication dict
    """
    login_id, trans_key = key.obtain(identifier)
    return {"merchantAuthentication": {"name": login_id, "transactionKey": trans_key}}


async def request(
    auth: dict, verb: str, fields: dict, connection: httpx.AsyncClient = None,
) -> httpx.Response:
    """Abstraction function for calling Authorize.net API methods.

    Args:
        auth: dict with login_id and transaction key
        verb: the request keyword to use, per Authorize.net instructions
        fields: the dict of fields and values to upload
        connection: optional async client

    Returns:
        Response
    """
    url = "https://api.authorize.net/xml/v1/request.api"
    payload = {verb: {**auth, **fields}}

    if connection:
        close_client = False
    else:
        connection = httpx.AsyncClient()
        close_client = True

    result = await connection.post(url, json=payload)
    result.encoding = "utf-8-sig"

    if close_client:
        await connection.aclose()

    return result


async def get_subscription(
    auth: dict, sub_id: str, connection: httpx.AsyncClient
) -> httpx.Response:
    """Get full info about a specific ARB subscription.

    Args:
        auth: dict with login_id and transaction key
        sub_id: ARB subscription id
        connection: optional async client

    Returns:
        Subscription and profile info as dict
    """
    fields = {"subscriptionId": sub_id}
    response = await request(auth, "ARBGetSubscriptionRequest", fields, connection)
    return response


async def get_subscriptions(auth: dict, sub_ids: typing.Iterable) -> typing.Iterable:
    """Get full info about specific ARB subscriptions.

    Args:
        auth: dict with login_id and transaction key
        sub_ids: list of ARB subscription ids

    Returns:
        Iterable of subscription and profile info
    """
    async with httpx.AsyncClient() as connection:
        tasks = [get_subscription(auth, sub_id, connection) for sub_id in sub_ids]
        responses = await asyncio.gather(*tasks)
    return (response.json()["subscription"] for response in responses)
