"""This module provides various gauges for observing voting power."""

# cspell: words pydantic

from dataclasses import dataclass

from prometheus_client import Gauge

from ..client import ApiClient

VOTING_POWER_RANGE_VOTERS = Gauge(
    "voting_power_range_voters",
    "Total number of voters in fixed ranges of voting power",
    ["range"],
)

VOTING_POWER_RANGE_SUM = Gauge(
    "voting_power_range_sum",
    "Sum of voting power in fixed ranges of voting power",
    ["range"],
)

VOTING_POWER_TOTAL = Gauge(
    "voting_power_total",
    "Total voting power",
)


@dataclass
class Bucket:
    """A bucket for a range of voting power.

    Attributes:
        min (int): The minimum voting power.
        max (int): The maximum voting power.
        power (int): The sum of voting power in this bucket.
        voters (int): The number of voters in this bucket.
    """

    min: int
    max: int
    power: int
    voters: int


async def scrape(client: ApiClient):
    """Scrape the voting power of all voters and update the gauges.

    Args:
        client (ApiClient): The API client to use.
    """
    voters = await client.get_voters()

    bucket_ranges = [
        (0, 1000),
        (1000, 10000),
        (10000, 100000),
        (100000, 1000000),
        (1000000, 10000000),
        (10000000, float("inf")),
    ]

    buckets: list[Bucket] = []
    for range in bucket_ranges:
        buckets.append(Bucket(range[0], range[1], 0, 0))

    for bucket in buckets:
        for voter in voters.values():
            if bucket.min <= voter.data.value < bucket.max:
                bucket.voters += 1
                bucket.power += voter.data.value

    for bucket in buckets:
        VOTING_POWER_RANGE_VOTERS.labels(f"{bucket.min}-{bucket.max}").set(
            bucket.voters
        )
        VOTING_POWER_RANGE_SUM.labels(f"{bucket.min}-{bucket.max}").set(
            bucket.power
        )

    VOTING_POWER_TOTAL.set(sum([bucket.power for bucket in buckets]))
