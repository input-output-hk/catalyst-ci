"""This module provides the number of unique voters (wallets)."""

# cspell: words pydantic

from prometheus_client import Gauge

from ..client import ApiClient

NUM_PROPOSAL_VOTES = Gauge(
    "num_proposal_votes",
    "The number of votes for a proposal",
    ["proposal_title"],
)

PROPOSAL_VOTING_POWER_TOTAL = Gauge(
    "proposal_voting_power_total",
    "Total voting power for a proposal",
    ["proposal_title"],
)


async def scrape(client: ApiClient):
    """Scrape the number of unique voters (wallets) and update the gauge.

    Args:
        client (ApiClient): The API client to use.
    """
    proposals = await client.get_proposals()
    plans = await client.get_active_plans()
    voters = await client.get_voters()

    # Index proposals by vote plan ID and proposal index
    proposals_by_index = {}
    for proposal in proposals.values():
        if proposal.chain_voteplan_id not in proposals_by_index:
            proposals_by_index[proposal.chain_voteplan_id] = {}

        proposals_by_index[proposal.chain_voteplan_id][
            proposal.chain_proposal_index
        ] = proposal

    # Calculate the voting power for each proposal by summing the voting power
    # of all voters who voted for it
    proposals_power = {}
    for voter in voters.values():
        for vote_plan_id, votes in voter.votes.items():
            for vote in votes:
                proposal = proposals_by_index[vote_plan_id][vote]
                proposals_power[proposal.chain_proposal_id] = (
                    proposals_power.get(proposal.chain_proposal_id, 0)
                    + voter.data.value
                )

    for plan in plans:
        for proposal in plan.proposals:
            proposal_title = proposals[proposal.proposal_id].proposal_title
            NUM_PROPOSAL_VOTES.labels(proposal_title).set(proposal.votes_cast)
            if proposal.proposal_id in proposals_power:
                PROPOSAL_VOTING_POWER_TOTAL.labels(proposal_title).set(
                    proposals_power[proposal.proposal_id]
                )
            else:
                PROPOSAL_VOTING_POWER_TOTAL.labels(proposal_title).set(0)
