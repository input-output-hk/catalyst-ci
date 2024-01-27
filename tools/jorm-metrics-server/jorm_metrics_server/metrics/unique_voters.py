"""This module provides the number of unique voters (wallets)."""

from prometheus_client import Gauge
from pydantic import BaseModel

from ..client import ApiClient


class AccountVotes(BaseModel):
    """The response from the /api/v1/votes/plan/accounts-votes-count endpoint.

    Attributes:
        votes (dict[str, int]): The number of votes per wallet.
    """

    votes: dict[str, int]


NUM_UNIQUE_VOTERS = Gauge(
    "num_unique_voters", "The number of unique voters (wallets)"
)


async def scrape(client: ApiClient):
    """Scrape the number of unique voters (wallets).

    Args:
        client (ApiClient): The API client to use.
    """
    resp = AccountVotes.model_validate(
        {"votes": await client.get("api/v1/votes/plan/accounts-votes-count")}
    )
    NUM_UNIQUE_VOTERS.set(len(resp.votes.keys()))
