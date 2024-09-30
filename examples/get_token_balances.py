from eth_rpc import EventData
from eth_rpc.types import BlockReference, primitives
from eth_rpc.utils import address_to_topic
from eth_typeshed.erc20 import ERC20, TransferEvent, TransferEventType
from eth_typeshed.multicall import multicall
from eth_typing import HexAddress, HexStr


async def get_tokens_held(address: HexAddress, start_block=0):
    topic = address_to_topic(address)
    transfers: list[EventData[TransferEventType]] = []
    async for event in TransferEvent.set_filter(topic1=topic).backfill(start_block):
        transfers.append(event)
    async for event in TransferEvent.set_filter(topic1=None, topic2=topic).backfill(
        start_block
    ):
        transfers.append(event)

    tokens = set([event.log.address for event in transfers])

    return tokens


async def get_balance_at_block(
    address: HexAddress,
    tokens: list[HexAddress],
    block_number: BlockReference = "latest",
):
    calls = [
        ERC20(address=token_address).balance_of(primitives.address(address))
        for token_address in tokens
    ]
    results = await multicall.try_execute(*calls, block_number=block_number)
    return {
        address: balance.result
        for address, balance in zip(tokens, results)
        if balance.success and balance.result
    }


async def get_all_balances(address: HexAddress):
    tokens = await get_tokens_held(address)
    return await get_balance_at_block(address, tokens)


if __name__ == "__main__":
    import asyncio
    import os

    from eth_rpc import set_alchemy_key

    set_alchemy_key(os.environ["ALCHEMY_KEY"])
    print(
        asyncio.run(
            get_all_balances(
                HexAddress(HexStr("0xf977814e90da44bfa03b6295a0616a897441acec"))
            )
        )
    )
