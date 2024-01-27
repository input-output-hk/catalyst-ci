"""This module provides the number of unique voters (wallets)."""

# cspell: words pydantic

from prometheus_client import Gauge

from ..client import ApiClient

NUM_PROPOSAL_VOTES = Gauge(
    "num_proposal_votes",
    "The number of votes for a proposal",
    ["proposal_title"],
)


async def scrape(client: ApiClient):
    """Scrape the number of unique voters (wallets) and update the gauge.

    Args:
        client (ApiClient): The API client to use.
    """
    proposals = await client.get_proposals()
    plans = await client.get_active_plans()

    i = 0
    for plan in plans:
        for proposal in plan.proposals:
            proposal_title = proposals[proposal.proposal_id].proposal_title
            NUM_PROPOSAL_VOTES.labels(proposal_title).set(proposal.votes_cast)
            i += 1
    print(i)
