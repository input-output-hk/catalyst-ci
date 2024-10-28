"""This module provides a model for representing an active voter."""

# cspell: words pydantic

from pydantic import BaseModel

from .account_by_id import AccountByID


class Voter(BaseModel):
    """Represents an active voter (wallet) that has at least one vote.

    Attributes:
        id (str): The ID of the voter.
        power (int): The voting power of the voter.
        votes (list[Proposal]):
            A dictionary of vote plan IDs and the proposals the voter has voted
            on.
    """

    id: str
    data: AccountByID
    votes: dict[str, list[int]]
