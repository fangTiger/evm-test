# evm-test

Utilities and a small CLI for interacting with EVM compatible networks via
HTTP JSON-RPC. The project uses [web3.py](https://github.com/ethereum/web3.py)
under the hood to offer a thin layer of ergonomics around common operations.

## Installation

Create a virtual environment and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Library usage

```python
from evm_client import EVMClient

client = EVMClient("https://rpc.sepolia.org")
print("Chain ID:", client.chain_id())
print("Latest block:", client.block_number())
balance = client.get_balance("0x00000000219ab540356cBB839Cbe05303d7705Fa")
print("Balance (wei):", balance.wei)
print("Balance (ether):", balance.ether)
```

## Command line interface

The `evm_cli.py` script exposes a few helper commands. All commands require the
RPC endpoint as the first argument.

Show provider information:

```bash
python evm_cli.py https://rpc.sepolia.org info
```

Display the balance of an address:

```bash
python evm_cli.py https://rpc.sepolia.org balance 0x00000000219ab540356cBB839Cbe05303d7705Fa
```

Query the transaction count for an address:

```bash
python evm_cli.py https://rpc.sepolia.org tx-count 0x00000000219ab540356cBB839Cbe05303d7705Fa
```

Call an arbitrary RPC method:

```bash
python evm_cli.py https://rpc.sepolia.org call eth_chainId
python evm_cli.py https://rpc.sepolia.org call eth_getBlockByNumber "\"latest\"" false
```
