"""High level helper for Ethereum JSON-RPC interactions."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Optional

from web3 import Web3
from web3.types import BlockIdentifier, ChecksumAddress, Wei


class RPCConnectionError(RuntimeError):
    """Raised when the client cannot connect to the RPC endpoint."""


@dataclass(frozen=True)
class Balance:
    """Represents an account balance in both wei and ether."""

    wei: Wei
    ether: Decimal


class EVMClient:
    """Convenience wrapper around :class:`web3.Web3`.

    Parameters
    ----------
    endpoint_url:
        The HTTP endpoint for the JSON-RPC provider. For example
        ``https://mainnet.infura.io/v3/<api-key>``.
    timeout:
        Optional timeout in seconds for RPC requests. The default is defined by
        the provider implementation.
    """

    def __init__(self, endpoint_url: str, *, timeout: Optional[int] = None) -> None:
        request_kwargs: Dict[str, Any] = {}
        if timeout is not None:
            request_kwargs["timeout"] = timeout

        provider = Web3.HTTPProvider(endpoint_url, request_kwargs=request_kwargs)
        self._web3 = Web3(provider)

        if not self._web3.is_connected():
            raise RPCConnectionError(
                "Unable to connect to the RPC endpoint. Check the URL and network connectivity."
            )

    @property
    def web3(self) -> Web3:
        """Expose the underlying :class:`Web3` instance."""

        return self._web3

    def chain_id(self) -> int:
        """Return the numeric chain ID reported by the provider."""

        return self._web3.eth.chain_id

    def block_number(self) -> int:
        """Return the current block number."""

        return self._web3.eth.block_number

    def get_balance(
        self, address: str, *, block_identifier: BlockIdentifier = "latest"
    ) -> Balance:
        """Fetch the balance for the given ``address``.

        Parameters
        ----------
        address:
            Either a checksummed address or any hexadecimal address that can be
            converted into one. The method will normalise the address to a
            checksum address before performing the RPC call.
        block_identifier:
            Optional block identifier. Defaults to ``"latest"``.
        """

        checksum: ChecksumAddress = self._web3.to_checksum_address(address)
        wei_balance: Wei = self._web3.eth.get_balance(checksum, block_identifier)
        ether_value: Decimal = self._web3.from_wei(wei_balance, "ether")
        return Balance(wei=wei_balance, ether=ether_value)

    def get_transaction_count(
        self, address: str, *, block_identifier: BlockIdentifier = "latest"
    ) -> int:
        """Return the number of transactions sent from ``address``."""

        checksum: ChecksumAddress = self._web3.to_checksum_address(address)
        return self._web3.eth.get_transaction_count(checksum, block_identifier)

    def call_method(self, method: str, *params: Any) -> Any:
        """Invoke an arbitrary RPC method.

        This is a thin wrapper around :meth:`web3.Web3.manager.request_blocking`
        that exposes low-level functionality without having to access the
        private manager attribute from user code.
        """

        return self._web3.manager.request_blocking(method, params)


__all__ = ["EVMClient", "RPCConnectionError", "Balance"]
