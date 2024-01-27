"""This module provides a client for interacting with the Jormungandr API."""

# cspell: words aiohttp

from typing import Any
from urllib.parse import urljoin

import aiohttp


class ApiClient:
    """A client for interacting with the Jormungandr API.

    Attributes:
        base_url (str): The base URL of the Jormungandr API.
        session (aiohttp.ClientSession): The HTTP session used for requests.
    """

    base_url: str
    session: aiohttp.ClientSession

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = aiohttp.ClientSession()

    async def get(self, path: str) -> Any:
        """Make a GET request to the Jormungandr API.

        Args:
            path (str): The relative path to request.

        Returns:
            Any: The response from the Jormungandr API.
        """
        async with self.session.get(urljoin(self.base_url, path)) as response:
            return await response.json()

    async def close(self):
        """Closes the web client."""
        await self.session.close()
