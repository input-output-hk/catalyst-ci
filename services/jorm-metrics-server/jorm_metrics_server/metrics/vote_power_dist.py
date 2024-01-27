"""This module provides a histogram of voting power."""

# cspell: words pydantic

from prometheus_client import Histogram

from ..client import ApiClient

VOTING_POWER_HISTOGRAM = Histogram(
    "voting_power",
    "Histogram of Voting Power",
    buckets=[0, 1000, 10000, 100000, 1000000, 10000000],
)


async def scrape(client: ApiClient):
    """Scrape the voting power of all voters and update the histogram.

    Args:
        client (ApiClient): The API client to use.
    """
    voters = await client.get_voters()
    for voter in voters.values():
        VOTING_POWER_HISTOGRAM.observe(voter.data.value)
