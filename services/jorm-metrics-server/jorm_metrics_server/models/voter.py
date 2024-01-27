from pydantic import BaseModel

from .account_by_id import AccountByID


class Voter(BaseModel):
    """Represents an active voter (wallet) that has at least one vote.

    Attributes:
        id (str): The ID of the voter.
        power (int): The voting power of the voter.
        votes (list[Proposal]):
            A list of proposals ids that the voter has voted on.
    """

    id: str
    data: AccountByID
    votes: list[int]
