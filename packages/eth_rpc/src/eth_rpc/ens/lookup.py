from eth_hash.auto import keccak
from eth_rpc.contract import ContractFunc, ProtocolBase
from eth_rpc.networks.ethereum import Ethereum
from eth_rpc.types import METHOD, BlockReference, Network, primitives


class ENSRegistryWithFallback(ProtocolBase):
    resolver: ContractFunc[
        primitives.bytes32,
        primitives.address,
    ] = METHOD


class Resolver(ProtocolBase):
    addr: ContractFunc[
        primitives.bytes32,
        primitives.address,
    ] = METHOD


async def lookup_addr(
    name: str,
    block_number: BlockReference = "latest",
    network: type[Network] = Ethereum,
):
    hashed_name = hash_ens_name(name)

    registry = ENSRegistryWithFallback(address=network.ens_registry)
    resolver_address = await registry.resolver(hashed_name).get(
        block_number=block_number
    )

    resolver = Resolver(address=resolver_address)
    return await resolver.addr(hashed_name).get(block_number=block_number)


def hash_ens_name(name: str):
    node = b"\0" * 32
    labels = name.split(".")
    for label in reversed(labels):
        labelhash = keccak(label.encode("utf-8"))
        assert isinstance(labelhash, bytes)
        assert isinstance(node, bytes)
        node = keccak(node + labelhash)
    return node
