"""This module provides the number of unique voters (wallets)."""

# cspell: words pydantic

from prometheus_client import Gauge

from ..client import ApiClient

NUM_UNIQUE_VOTERS = Gauge(
    "num_unique_voters", "The number of unique voters (wallets)"
)


async def scrape(client: ApiClient):
    """Scrape the number of unique voters (wallets) and update the gauge.

    Args:
        client (ApiClient): The API client to use.
    """
    NUM_UNIQUE_VOTERS.set(len(await client.get_voters()))
