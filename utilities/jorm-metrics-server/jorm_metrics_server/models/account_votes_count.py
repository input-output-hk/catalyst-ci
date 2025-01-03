"""This module provides a model for the /api/v1/votes/plan/accounts-votes-count
endpoint."""

# cspell: words pydantic

from pydantic import BaseModel


class AccountVotesCount(BaseModel):
    """The response from the /api/v1/votes/plan/accounts-votes-count endpoint.

    Attributes:
        votes (dict[str, int]): The number of votes per wallet.
    """

    votes: dict[str, int]
