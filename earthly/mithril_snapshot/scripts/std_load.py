#!/usr/bin/env python3

# cspell: words

import python.exec_manager as exec_manager
import argparse
import rich
from rich import print
import os
import enum

# This script loads latest mithril snapshot archive


class NetworkType(enum.Enum):
    Mainnet = "mainnet"
    Testnet = "testnet"
    Preprod = "preprod"
    Preview = "preview"

    def get_aggregator_url(self):
        if self == NetworkType.Mainnet:
            return "https://aggregator.release-mainnet.api.mithril.network/aggregator"
        if self == NetworkType.Testnet:
            return "https://aggregator.testing-preview.api.mithril.network/aggregator"
        if self == NetworkType.Preprod:
            return "https://aggregator.release-preprod.api.mithril.network/aggregator"
        if self == NetworkType.Preview:
            return (
                "https://aggregator.pre-release-preview.api.mithril.network/aggregator"
            )

    # taken from https://github.com/input-output-hk/mithril/tree/main/mithril-infra/configuration
    def get_genesis_verification_key(self):
        if self == NetworkType.Mainnet:
            return "5b3139312c36362c3134302c3138352c3133382c31312c3233372c3230372c3235302c3134342c32372c322c3138382c33302c31322c38312c3135352c3230342c31302c3137392c37352c32332c3133382c3139362c3231372c352c31342c32302c35372c37392c33392c3137365d"
        if self == NetworkType.Testnet:
            return "5b3132372c37332c3132342c3136312c362c3133372c3133312c3231332c3230372c3131372c3139382c38352c3137362c3139392c3136322c3234312c36382c3132332c3131392c3134352c31332c3233322c3234332c34392c3232392c322c3234392c3230352c3230352c33392c3233352c34345d"
        if self == NetworkType.Preprod:
            return "5b3132372c37332c3132342c3136312c362c3133372c3133312c3231332c3230372c3131372c3139382c38352c3137362c3139392c3136322c3234312c36382c3132332c3131392c3134352c31332c3233322c3234332c34392c3232392c322c3234392c3230352c3230352c33392c3233352c34345d"
        if self == NetworkType.Preview:
            return "5b3132372c37332c3132342c3136312c362c3133372c3133312c3231332c3230372c3131372c3139382c38352c3137362c3139392c3136322c3234312c36382c3132332c3131392c3134352c31332c3233322c3234332c34392c3232392c322c3234392c3230352c3230352c33392c3233352c34345d"


def main():
    # Force color output in CI
    rich.reconfigure(color_system="256")

    parser = argparse.ArgumentParser(description="Mithril snapshot loading.")
    parser.add_argument(
        "--network",
        type=NetworkType,
        help="Cardano network type, available options: ['mainnet', 'testnet', 'preprod', 'preview']",
    )
    args = parser.parse_args()

    results = exec_manager.Results("Mithril snapshot loading.")

    # download latest snapshot
    results.add(
        exec_manager.cli_run(
            " ".join(
                [
                    f"GENESIS_VERIFICATION_KEY={args.network.get_genesis_verification_key()}",
                    f"AGGREGATOR_ENDPOINT={args.network.get_aggregator_url()}",
                    "mithril-client",
                    "cardano-db",
                    "download",
                    "latest",
                ]
            ),
            name=f"Dowload latest mithril snapshot for {args.network}",
        )
    )

    results.print()
    if not results.ok():
        exit(1)


if __name__ == "__main__":
    main()
