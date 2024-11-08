"""This module provides a model for the /api/v0/proposals endpoint."""

from pydantic import BaseModel

# cspell: words pydantic voteplan


class ProposalProposer(BaseModel):
    """A proposal proposer."""

    proposer_name: str
    proposer_email: str
    proposer_url: str
    proposer_relevant_experience: str


class ProposalCategory(BaseModel):
    """A proposal category."""

    category_id: str
    category_name: str
    category_description: str


class Proposal(BaseModel):
    """A proposal."""

    internal_id: int
    proposal_id: int
    proposal_category: ProposalCategory
    proposal_title: str
    proposal_summary: str
    proposal_solution: str
    proposal_public_key: str
    proposal_funds: int
    proposal_url: str
    proposal_files_url: str
    proposal_impact_score: int
    proposer: ProposalProposer
    chain_proposal_id: str
    chain_vote_options: dict[str, int]
    chain_vote_start_time: str
    chain_vote_end_time: str
    chain_committee_end_time: str
    chain_voteplan_payload: str
    chain_vote_encryption_key: str
    fund_id: int
    challenge_id: int
    reviews_count: int
    chain_voteplan_id: str
    chain_proposal_index: int
    challenge_type: str
