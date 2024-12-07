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


if __name__ == "__main__":
    import asyncio

    async def amain():
        tx = await Transaction.load(id="dda726e3dad9504dce5098dfab5064ecd4a7650bfe854bb2606da3152b60e427")

        print("Tx:", tx)

        for input in tx.inputs:
            print("\t INPUT: ", input)
            print("\t scrypt:", input.script_sig.asm)
            print("\t value:", await input.value())
            print("\n")

    asyncio.run(amain())
