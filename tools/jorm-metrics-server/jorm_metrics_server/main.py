"""Jormungandr metrics server."""

import asyncio
import sys

import asyncclick as click
from aiohttp import web as aiohttp_web
from loguru import logger
from prometheus_async.aio import web

from .metrics import unique_voters
from .scraper import Scraper


async def scrape(api_url: str, interval: int):
    """Scrape metrics from the Jormungandr API.

    Args:
        api_url (str): The URL of the Jormungandr API.
        interval (int): The scraping interval in seconds.
    """
    logger.info("Starting scraping loop")

    scraper = Scraper(api_url)
    scraper.register(unique_voters.scrape)

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
    "--disable-json",
    is_flag=True,
    help="Disable outputting logs in JSON format.",
    default=False,
    envvar="DISABLE_JSON_LOGS",
)
async def main(
    address: str, port: int, api_url: str, interval: int, disable_json: bool
):
    logger.remove()
    logger.add(sys.stderr, serialize=not disable_json)

    tasks = [scrape(api_url, interval), serve_metrics(address, port)]

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
