"""This module provides a model for the /api/v0/account/account_id endpoint."""

# cspell: words pydantic

from typing import Any

from pydantic import BaseModel


class Delegation(BaseModel):
    """Information about delegation.

    Attributes:
        pools (list[list[Any]]): The list of pools the account has delegated.
    """

    pools: list[list[Any]]


class LastRewards(BaseModel):
    """The last reward received by the account.

    Attributes:
        epoch (int): The epoch the reward was received.
        reward (int): The reward received.
    """

    epoch: int
    reward: int


class AccountByID(BaseModel):
    """The response from the /api/v0/account/account_id endpoint.

    Attributes:
        counters (list[int]):
            An array of corresponding spending counters to the account.
        delegation (Delegation): Information about delegation.
        last_reward (LastReward): The last reward received by the account.
        tokens (dict[str, int]):
            Current state of the token balances of this account
        votes (dict[str, int]): The number of votes per wallet.
    """

    counters: list[int]
    delegation: Delegation
    last_rewards: LastRewards
    tokens: dict[str, int]
    value: int
