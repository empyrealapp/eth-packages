from eth_rpc.types import BlockExplorer, Network, Rpcs, RpcUrl
from pydantic.networks import Url


class Arbitrum(Network):
    chain_id = 42161
    name = "Arbitrum"
    native_currency = "ETH"
    rpc = Rpcs(
        default=RpcUrl(
            http=Url("https://arb1.arbitrum.io/rpc"),
        )
    )
    block_explorer = BlockExplorer(
        name="Arbiscan",
        url="https://arbiscan.io",
        api_url="https://api.arbiscan.io/api",
    )
    alchemy_str = "arb-mainnet"
    apprx_block_time = 0.26


# Arbitrum = Network(
#     chain_id=42161,
#     name="Arbitrum",
#     native_currency="ETH",
#     rpc=Rpcs(
#         default=RpcUrl(
#             http=Url("https://arb1.arbitrum.io/rpc"),
#             wss=None,
#             # wss=Url("wss://test.com"),
#         )
#     ),
#     block_explorer=BlockExplorer(
#         name="Arbiscan",
#         url="https://arbiscan.io",
#         api_url="https://api.arbiscan.io/api",
#     ),
#     alchemy_str="arb-mainnet",
#     apprx_block_time=0.26,
# )


# def as_type(network: Network):
#     impl = f"""
# class {network.name}:
#     chain_id = {network.chain_id}
#     name = {network.name}
#     native_currency = {network.native_currency}
#     rpc = {network.rpc}
#     block_explorer = {network.block_explorer}
#     alchemy_str: str | None = {network.alchemy_str}
#     multicall3: HexAddress | None = "{network.multicall3}"
#     ens_registry: HexAddress | None = "{network.ens_registry}"
#     ens_universal_resolver = "{network.ens_universal_resolver}"
#     apprx_block_time = {network.apprx_block_time}
# """
