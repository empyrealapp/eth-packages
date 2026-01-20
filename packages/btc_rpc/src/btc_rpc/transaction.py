from typing import Literal

from eth_typing import HexStr

from btc_rpc.types import GetTxRequest, Verbose2Transaction
from ._request import Request


class Transaction(Verbose2Transaction, Request):
    @classmethod
    async def load(self, id: HexStr, verbosity: Literal[0, 1, 2] = 2) -> "Transaction":
        rpc = self._rpc()
        return await rpc.get_raw_transaction(
            GetTxRequest(
                txid=id,
                verbose=verbosity,
            )
        )

    def get_lineage(self):
        pass
