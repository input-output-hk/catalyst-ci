"""This module provides a client for interacting with the Jormungandr API."""

# cspell: words aiohttp loguru pydantic

import asyncio
import os
from typing import Any
from urllib.parse import urljoin

import aiohttp
from loguru import logger
from pydantic import TypeAdapter

from .models.account_by_id import AccountByID
from .models.account_votes import AccountVotes
from .models.account_votes_count import AccountVotesCount
from .models.active_plans import VotePlan
from .models.proposals import Proposal
from .models.voter import Voter


class ApiClient:
    """A client for interacting with the Jormungandr API.

    Attributes:
        base_url (str): The base URL of the Jormungandr API.
        session (aiohttp.ClientSession): The HTTP session used for requests.
        storage (str): A path to a directory to store cached data.
    """

    base_url: str
    session: aiohttp.ClientSession
    storage: str

    _proposals_cache: dict[int, Proposal]
    _proposals_cache_path: str

    _voter_cache: dict[str, Voter]
    _voter_cache_path: str

    def __init__(self, base_url: str, storage: str):
        self.base_url = base_url
        self.session = aiohttp.ClientSession()
        self.storage = storage

        self._proposals_cache_path = os.path.join(storage, "proposals.json")
        self._voter_cache_path = os.path.join(storage, "voters.json")

        adapter = TypeAdapter(dict[str, Voter])
        if os.path.exists(self._voter_cache_path):
            with open(self._voter_cache_path) as f:
                self._voter_cache = adapter.validate_json(f.read())
        else:
            self._voter_cache = {}

        adapter = TypeAdapter(dict[str, Proposal])
        if os.path.exists(self._proposals_cache_path):
            with open(self._proposals_cache_path) as f:
                self._proposals_cache = adapter.validate_json(f.read())
        else:
            self._proposals_cache = {}

    async def close(self):
        """Closes the web client."""
        await self.session.close()

    async def get(self, path: str) -> Any:
        """Make a GET request to the Jormungandr API.

        Args:
            path (str): The relative path to request.

        Returns:
            Any: The response from the Jormungandr API.
        """
        async with self.session.get(urljoin(self.base_url, path)) as response:
            return await response.json()

    async def get_account_by_id(self, account_id: str) -> AccountByID:
        """Get the account information for a given account ID.

        Args:
            account_id (str): The account ID to get information for.

        Returns:
            Any: The account information for the given account ID.
        """
        return AccountByID.model_validate(
            await self.get(f"api/v0/account/{account_id}")
        )

    async def get_account_votes(self, account_id: str) -> dict[str, list[int]]:
        """Get the proposal internal IDs that the account has voted on.

        Args:
            account_id (str): The account ID to get votes for.

        Returns:
            dict[str, list[int]]:
                A dictionary of vote plan IDs and the proposals the account
                has voted on.
        """
        adapter = TypeAdapter(list[AccountVotes])
        resp = adapter.validate_python(
            await self.get(f"api/v1/votes/plan/account-votes/{account_id}")
        )

        votes = {}
        for r in resp:
            votes[r.vote_plan_id] = r.votes

        return votes

    async def get_accounts_votes(self) -> AccountVotesCount:
        """Get the number of votes per wallet.

        Returns:
            AccountVotes: The number of votes per wallet.
        """
        return AccountVotesCount.model_validate(
            {"votes": await self.get("api/v1/votes/plan/accounts-votes-count")}
        )

    async def get_active_plans(self) -> list[VotePlan]:
        """Get all active plans.

        Returns:
            list[VotePlan]: All active plans.
        """
        adapter = TypeAdapter(list[VotePlan])
        return adapter.validate_python(
            await self.get("api/v0/vote/active/plans")
        )

    async def get_proposals(self) -> dict[str, Proposal]:
        """Get all proposals.

        Returns:
            list[Proposal]: All proposals.
        """
        if self._proposals_cache:
            return self._proposals_cache

        adapter = TypeAdapter(list[Proposal])
        proposals_data = adapter.validate_python(
            await self.get("api/v0/proposals")
        )
        for proposal in proposals_data:
            self._proposals_cache[proposal.chain_proposal_id] = proposal

        adapter = TypeAdapter(dict[str, Proposal])
        with open(self._proposals_cache_path, "wb") as f:
            f.write(adapter.dump_json(self._proposals_cache))

        return self._proposals_cache

    async def get_proposal_by_id(self, id: int) -> Proposal:
        """Get a proposal by its internal ID.

        Args:
            id (int): The internal ID of the proposal to get.

        Returns:
            Proposal: The proposal with the given internal ID.
        """
        return (await self.get_proposals())[id]

    async def get_voters(self) -> dict[str, Voter]:
        """Get all voters that have voted.

        Note that this method uses a cache to avoid making too many requests to
        the Jormungandr API. It will only make requests for voters that are
        not already in the cache.

        Returns:
            dict[str, Voter]: A dictionary of voters
        """
        accounts_ids = (await self.get_accounts_votes()).votes.keys()
        tasks = []
        for account_id in accounts_ids:
            if account_id not in self._voter_cache:
                tasks.append(
                    asyncio.create_task(self.update_voter_cache(account_id))
                )

        await asyncio.gather(*tasks)

        adapter = TypeAdapter(dict[str, Voter])
        with open(self._voter_cache_path, "wb") as f:
            f.write(adapter.dump_json(self._voter_cache))

        return self._voter_cache

    async def update_voter_cache(self, account_id: str):
        """Update the voter cache for a given account ID.

        Args:
            account_id (str): The account ID to update the voter cache with.
        """
        logger.info(f"Fetching voter details for {account_id}")
        resp = await self.get_account_by_id(account_id)
        voter = Voter(
            id=account_id,
            data=resp,
            votes=await self.get_account_votes(account_id),
        )
        self._voter_cache[account_id] = voter
