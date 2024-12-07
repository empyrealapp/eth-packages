from typing import Literal

from eth_typing import HexStr

from btc_rpc.types import (
    GetBlockHashRequest,
    GetBlockRequest,
    GetTxRequest,
    Transaction,
    Block as BlockModel,
)
from ._request import Request


class Block(BlockModel, Request):
    @classmethod
    async def latest(cls, verbosity: Literal[0, 1, 2] = 2) -> "Block":
        rpc = cls._rpc()
        best_hash = await rpc.get_best_hash()
        return await cls.from_hash(hash=best_hash, verbosity=verbosity)

    @classmethod
    async def from_hash(cls, hash: HexStr, verbosity: Literal[0, 1, 2] = 2):
        rpc = cls._rpc()
        block = await rpc.get_block(
            GetBlockRequest(
                blockhash=hash,
                verbose=verbosity,
            ),
        )
        return block

    @classmethod
    async def get_block(cls, number: int, verbosity: Literal[0, 1, 2] = 1) -> "Block":
        rpc = cls._rpc()
        block_hash = await rpc.get_block_hash(
            GetBlockHashRequest(
                height=number,
            )
        )
        return await cls.from_hash(hash=block_hash, verbosity=verbosity)

    async def get_transactions(self, verbosity: Literal[0, 1, 2] = 1, blockhash: HexStr | None = None):
        txs = []
        rpc = self._rpc()
        for tx in self.txs:
            if isinstance(tx, Transaction):
                tx_id = tx.txid
            else:
                tx_id = tx
            txs.append(
                await rpc.get_raw_transaction(
                    GetTxRequest(
                        txid=tx_id,
                        verbose=verbosity,
                        blockhash=blockhash,
                    )
                )
            )
        return txs

    @classmethod
    async def load(self, number: int, verbosity: Literal[0, 1, 2] = 1) -> tuple["Block", list[Transaction]]:
        block = await self.get_block(number=number, verbosity=verbosity)
        txs = await block.get_transactions(verbosity=verbosity)
        return block, txs

    async def _transactions(self, verbosity: Literal[0, 1, 2] = 2):
        rpc = self._rpc()
        for tx in self.txs:
            if isinstance(tx, Transaction):
                tx_id = tx.txid
            else:
                tx_id = tx
            yield await rpc.get_raw_transaction(
                GetTxRequest(
                    txid=tx_id,
                    verbose=verbosity,
                    blockhash=self.hash,
                )
            )

    @property
    def transactions(self):
        return self._transactions()

    def __repr__(self):
        return f"<Block number={self.height}>"

    __str__ = __repr__
