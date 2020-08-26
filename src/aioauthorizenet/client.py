"""Simple POC Authorize.net API client."""

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


def request(auth: dict, verb: str, fields: dict) -> dict:
    """Abstraction function for calling Authorize.net API methods.

    Args:
        auth: dict with login_id and transaction key
        verb: the request keyword to use, per Authorize.net instructions
        fields: the dict of fields and values to upload

    Returns:
        Response body as a Python dict
    """
    url = "https://api.authorize.net/xml/v1/request.api"
    payload = {verb: {**auth, **fields}}
    result = httpx.post(url, json=payload)
    result.encoding = "utf-8-sig"
    return result.json()


def get_subscription(auth: dict, sub_id: str) -> dict:
    """Get full info about a specific ARB subscription.

    Args:
        auth: dict with login_id and transaction key
        sub_id: ARB subscription id as string

    Returns:
        Subscription and profile info as dict
    """
    fields = {"subscriptionId": sub_id}
    result = request(auth, "ARBGetSubscriptionRequest", fields)
    subscription = result["subscription"]
    profile = subscription["profile"]
    return {
        "customer_id": profile["customerProfileId"],
        "payment_id": profile["paymentProfile"]["customerPaymentProfileId"],
        "arb_start": subscription["paymentSchedule"]["startDate"][:10],
        "amount": subscription["amount"],
    }


def run() -> None:
    """Get subscription info."""
    import json  # noqa:SC100,C0415
    import sys  # noqa:SC100,C0415

    auth = authentication(sys.argv[1])
    sub_info = get_subscription(auth, sys.argv[2])
    print(json.dumps(sub_info, indent=2))
