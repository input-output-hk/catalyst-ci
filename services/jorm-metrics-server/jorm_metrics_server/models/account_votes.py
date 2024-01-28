"""
This module provides a model for the api/v1/votes/plan/account-votes endpoint.
"""

# cspell: words pydantic

from pydantic import BaseModel


class AccountVotes(BaseModel):
    """Account votes.

    Attributes:
        vote_plan_id (str): The ID of the vote plan.
        votes (list[int]):
            A list of proposal internal IDs that the account has voted on.
    """

    vote_plan_id: str
    votes: list[int]
