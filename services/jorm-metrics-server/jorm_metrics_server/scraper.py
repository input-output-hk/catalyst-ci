"""
This module provides a scraper for scraping metrics from the Jormungandr API.
"""

from typing import Callable

from .client import ApiClient


class Scraper:
    """A scraper for scraping metrics from the Jormungandr API.

    Attributes:
        client (ApiClient): The API client to use.
        metrics (list[Callable[[ApiClient], None]]):
            A list of metric scrape functions to call.
    """

    client: ApiClient
    metrics: Callable[[ApiClient], None]

    def __init__(self, api_url: str):
        self.client = ApiClient(api_url)
        self.metrics = []

    def register(self, metric: Callable[[ApiClient], None]):
        """Register a metric scrape function to call.

        Args:
            metric (Callable[[ApiClient], None]):
                The metric scrape function to call.
        """
        self.metrics.append(metric)

    async def scrape(self):
        """Run all registered metric scrape functions."""
        for metric in self.metrics:
            await metric(self.client)

    async def stop(self):
        """Stop the scraper and close any open connections."""
        await self.client.close()
