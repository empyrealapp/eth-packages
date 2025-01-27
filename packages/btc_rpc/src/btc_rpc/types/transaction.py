from typing import Literal

from eth_typing import HexStr

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from .primitives import BtcAddress
from btc_rpc._request import Request
from btc_rpc.utils import (
    CScript,
    CScriptTruncatedPushDataError,
    CScriptInvalidError,
    OP_FALSE,
    OP_IF,
    OP_ENDIF,
)


class ScriptSig(BaseModel):
    asm: HexStr
    hex: HexStr


class InVector(BaseModel, Request):
    txid: HexStr | None = None
    vout: int | None = None
    script_sig: ScriptSig | None = None
    sequence: int
    txinwitness: list[HexStr] | None = None
    coinbase: HexStr | None = None

    def _extract_ord(self, iterable):  # noqa: C901
        try:
            while next(iterable) != OP_FALSE:
                continue
        except (StopIteration, CScriptTruncatedPushDataError, CScriptInvalidError):
            return None
        try:
            if next(iterable) != OP_IF:
                return None
            if next(iterable) != b"ord":
                return None
        except (CScriptTruncatedPushDataError, CScriptInvalidError):
            return None
        d = {}
        while (key := next(iterable)) != 0:
            if key in d:
                return None
            value = next(iterable)
            d[key] = value
        d["data"] = b""
        while (data := next(iterable)) != OP_ENDIF:
            d["data"] += data
        return d

    def ord(self):
        ords = []
        if not self.txinwitness:
            return None
        if len(self.txinwitness) < 2:
            return None
        second_to_last = self.txinwitness[-2]
        iterable = iter(CScript.fromhex(second_to_last))
        while True:
            try:
                ord = self._extract_ord(iterable)
                if not ord:
                    break
                ords.append(ord)
            except StopIteration:
                break
        return ords

    async def transaction(self, verbosity: Literal[0, 1, 2] = 2):
        from btc_rpc.transaction import Transaction

        assert self.txid is not None
        return await Transaction.load(self.txid)

    async def lineage(self):
        from btc_rpc.block import Block

        input = self
        inputs = []
        while True:
            if input.coinbase:
                break
            tx, output = await input.prev()
            block = await Block.from_hash(tx.blockhash)
            input = tx.inputs[0]
            inputs.append(block.height)
        return inputs

    async def value(self) -> float:
        if not self.txid:
            return 0.0

        assert self.vout is not None
        tx = await self.transaction()
        output: OutVector = tx.outputs[self.vout]
        return output.value

    async def prev(self) -> "tuple[VerboseTransaction, OutVector] | None":
        from btc_rpc.transaction import Transaction

        if not self.txid:
            return None

        assert self.vout is not None
        tx = await Transaction.load(self.txid)
        output: OutVector = tx.outputs[self.vout]
        return tx, output

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    def __repr__(self):
        return f"<InVector txid={self.txid} vout={self.vout} sequence={self.sequence} coinbase={self.coinbase}>"

    __str__ = __repr__


class LockingCode(BaseModel):
    """scriptPubKey"""

    asm: str
    hex: str
    desc: str
    type: Literal[
        "pubkey",
        "pubkeyhash",
        "scripthash",
        "witness_v0_keyhash",
        "nulldata",
        "witness_v0_scripthash",
        "witness_v1_taproot",
        "multisig",
    ]
    address: BtcAddress | None = None


class OutVector(BaseModel):
    value: float
    n: int
    script_pub_key: LockingCode

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    def __repr__(self):
        return f"<OutVector value={self.value}>"

    __str__ = __repr__


class Transaction(BaseModel):
    txid: HexStr
    hash: HexStr
    version: int
    size: int
    vsize: int
    weight: int
    locktime: int
    inputs: list[InVector] = Field(alias="vin")
    outputs: list[OutVector] = Field(alias="vout")

    def __repr__(self):
        return f"<Transaction id={self.txid}>"

    __str__ = __repr__


class VerboseTransaction(Transaction):
    # optional
    hex: HexStr | None = None
    blockhash: HexStr | None = None
    confirmations: int | None = None
    time: int | None = None
    blocktime: int | None = None


class Verbose2Transaction(VerboseTransaction):
    fee: float | None = None
