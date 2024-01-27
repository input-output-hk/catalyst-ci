"""Jormungandr metrics server."""

# cspell: words asyncclick aiohttp loguru

import asyncio
import sys

import asyncclick as click
from aiohttp import web as aiohttp_web
from loguru import logger
from prometheus_async.aio import web

from .metrics import proposal_votes, unique_voters, vote_power_dist
from .scraper import Scraper

# Map of metric names to metric scrapers
METRIC_MAP = {
    "num_proposal_votes": proposal_votes.scrape,
    "num_unique_voters": unique_voters.scrape,
    "voting_power": vote_power_dist.scrape,
}


async def scrape(api_url: str, interval: int, storage: str, metrics: str):
    """Scrape metrics from the Jormungandr API.

    Args:
        api_url (str): The URL of the Jormungandr API.
        interval (int): The scraping interval in seconds.
    """
    logger.info("Starting scraping loop")

    scraper = Scraper(api_url, storage)
    for metric in metrics.split(","):
        if metric not in METRIC_MAP:
            logger.warning(f"Unknown metric: {metric}")
            continue
        scraper.register(METRIC_MAP[metric])

    try:
        while True:
            logger.info("Scraping metrics")
            await scraper.scrape()

            logger.info(f"Sleeping for {interval} seconds")
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        pass
    finally:
        await scraper.stop()


async def serve_metrics(address: str, port: int):
    """Serve metrics on the given address and port.

    Args:
        address (str): The address to serve metrics on.
        port (int): The port to serve metrics on.
    """
    app = aiohttp_web.Application()
    app.router.add_get("/metrics", web.server_stats)

    runner = aiohttp_web.AppRunner(app)
    await runner.setup()

    site = aiohttp_web.TCPSite(runner, address, port)
    await site.start()


@click.command()
@click.option(
    "--address",
    help="Address to serve metrics on.",
    default="0.0.0.0",
    envvar="ADDRESS",
)
@click.option(
    "--port", help="Port to serve metrics on.", default=8080, envvar="PORT"
)
@click.option(
    "--api-url",
    help="URL of the Jormungandr API.",
    required=True,
    envvar="API_URL",
)
@click.option(
    "--interval",
    help="Scraping interval in seconds.",
    default=60,
    envvar="INTERVAL",
)
@click.option(
    "--storage",
    help="A path to a directory where the metrics server will store a cache.",
    default="/tmp/cache",
    envvar="STORAGE",
)
@click.option(
    "--metrics",
    help="Comma-separated list of metrics to scrape.",
    default="num_proposal_votes,num_unique_voters,voting_power",
    envvar="METRICS",
)
@click.option(
    "--disable-json",
    is_flag=True,
    help="Disable outputting logs in JSON format.",
    default=False,
    envvar="DISABLE_JSON_LOGS",
)
async def main(
    address: str,
    port: int,
    api_url: str,
    interval: int,
    storage: str,
    metrics: str,
    disable_json: bool,
):
    logger.remove()
    logger.add(sys.stderr, serialize=not disable_json)

    tasks = [
        scrape(api_url, interval, storage, metrics),
        serve_metrics(address, port),
    ]

    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        for task in tasks:
            task.cancel()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Shutting down")
