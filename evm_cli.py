"""Command line helper for interacting with EVM networks."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

from web3.datastructures import AttributeDict

from evm_client import EVMClient, RPCConnectionError


def parse_args(argv: Any) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("endpoint", help="HTTP endpoint of the Ethereum JSON-RPC provider")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("info", help="Show provider information")

    balance_parser = subparsers.add_parser("balance", help="Display the account balance")
    balance_parser.add_argument("address", help="Ethereum address to inspect")
    balance_parser.add_argument(
        "--block",
        dest="block_identifier",
        default="latest",
        help="Block identifier (number or tag) to query. Default: latest",
    )

    tx_count_parser = subparsers.add_parser(
        "tx-count", help="Show the number of transactions sent from the address"
    )
    tx_count_parser.add_argument("address", help="Ethereum address to inspect")
    tx_count_parser.add_argument(
        "--block",
        dest="block_identifier",
        default="latest",
        help="Block identifier (number or tag) to query. Default: latest",
    )

    call_parser = subparsers.add_parser("call", help="Call an arbitrary RPC method")
    call_parser.add_argument("method", help="JSON-RPC method name")
    call_parser.add_argument(
        "params",
        nargs="*",
        help="Optional JSON encoded parameters. Provide strings that can be parsed with json.loads.",
    )

    return parser.parse_args(argv)


def _normalise(value: Any) -> Any:
    if isinstance(value, AttributeDict):
        return {k: _normalise(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalise(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_normalise(item) for item in value)
    if isinstance(value, bytes):
        return value.hex()
    if hasattr(value, "hex") and callable(getattr(value, "hex")):
        try:
            return value.hex()
        except TypeError:
            pass
    return value


def _load_params(params: Any) -> Any:
    parsed = []
    for value in params:
        try:
            parsed.append(json.loads(value))
        except json.JSONDecodeError:
            parsed.append(value)
    return parsed


def run_cli(argv: Any = None) -> int:
    args = parse_args(argv)
    try:
        client = EVMClient(args.endpoint)
    except RPCConnectionError as exc:  # pragma: no cover - exercised interactively
        print(f"Connection failed: {exc}", file=sys.stderr)
        return 1

    if args.command == "info":
        info: Dict[str, Any] = {
            "chain_id": client.chain_id(),
            "block_number": client.block_number(),
        }
        print(json.dumps(info, indent=2))
        return 0

    if args.command == "balance":
        balance = client.get_balance(args.address, block_identifier=args.block_identifier)
        info = {"wei": str(balance.wei), "ether": str(balance.ether)}
        print(json.dumps(info, indent=2))
        return 0

    if args.command == "tx-count":
        count = client.get_transaction_count(args.address, block_identifier=args.block_identifier)
        print(count)
        return 0

    if args.command == "call":
        params = _load_params(args.params)
        result = client.call_method(args.method, *params)
        print(json.dumps(_normalise(result), indent=2))
        return 0

    raise AssertionError(f"Unknown command: {args.command}")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(run_cli(sys.argv[1:]))
