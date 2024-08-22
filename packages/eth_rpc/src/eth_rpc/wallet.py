import secrets
from abc import ABC, abstractmethod
from typing import Literal, Optional

from eth_account import Account
from eth_account.account import LocalAccount
from eth_rpc.types import (
    BLOCK_STRINGS,
    CallWithBlockArgs,
    EthCallParams,
    GetAccountArgs,
    RawTransaction,
    SignedTransaction,
)
from eth_typing import HexAddress, HexStr

from ._request import Request
from ._transport import _force_get_global_rpc
from .block import Block
from .transaction import PreparedTransaction
from .types import HexInteger, RPCResponseModel


class BaseWallet(Request, ABC):
    address: HexAddress

    def get_nonce(self, block_number: int | BLOCK_STRINGS = "latest"):
        return RPCResponseModel(
            self._rpc().get_tx_count,
            GetAccountArgs(
                address=self.address,
                block_number=(
                    HexInteger(block_number)
                    if isinstance(block_number, int)
                    else block_number
                ),
            ),
        )

    @abstractmethod
    def sign_transaction(self, tx) -> SignedTransaction: ...

    @abstractmethod
    def send_raw_transaction(
        self, tx: HexStr
    ) -> RPCResponseModel[RawTransaction, HexStr]: ...


class MockWallet(BaseWallet):
    def __init__(self, address: HexAddress):
        self.address = address

    def sign_transaction(self, tx):
        raise NotImplementedError("Mock wallet can not sign")


class PrivateKeyWallet(BaseWallet):
    account: LocalAccount

    @staticmethod
    def get_pvt_key() -> HexStr:
        priv = secrets.token_hex(32)
        return HexStr(f"0x{priv}")

    @classmethod
    def create_new(cls):
        return cls(cls.get_pvt_key())

    @property
    def address(self) -> HexAddress:  # type: ignore
        return self.account.address

    def __init__(self, private_key: HexStr):
        self.account = Account.from_key(private_key)

    def sign_transaction(self, tx: PreparedTransaction) -> SignedTransaction:
        signed_tx = self.account.sign_transaction(tx.model_dump())
        return SignedTransaction(
            raw_transaction=signed_tx[0].hex(),
            hash=signed_tx.hash.hex(),
            r=signed_tx.r,
            s=signed_tx.s,
            v=signed_tx.v,
        )

    def send_raw_transaction(
        self, tx: HexStr
    ) -> RPCResponseModel[RawTransaction, HexStr]:
        return RPCResponseModel(
            self._rpc().send_raw_tx,
            RawTransaction(
                signed_tx=tx,
            ),
        )

    def prepare_and_sign(
        self,
        *,
        to: HexAddress,
        value: int = 0,
        max_fee_per_gas: Optional[int] = None,
        max_priority_fee_per_gas: Optional[int] = None,
        data: HexStr = HexStr("0x"),
        nonce: Optional[int] = None,
    ):
        prepared = self.prepare(
            to=to,
            value=value,
            max_fee_per_gas=max_fee_per_gas,
            max_priority_fee_per_gas=max_priority_fee_per_gas,
            data=data,
            nonce=nonce,
        )
        return self.sign_transaction(prepared)

    def prepare(
        self,
        *,
        to: HexAddress,
        value: int = 0,
        max_fee_per_gas: Optional[int] = None,
        max_priority_fee_per_gas: Optional[int] = None,
        data: HexStr = HexStr("0x"),
        nonce: Optional[int] = None,
    ):
        # TODO: this assumes sync
        gas = self.estimate_gas(to=to, data=data).sync
        access_list = None
        rpc = _force_get_global_rpc()
        chain_id = rpc.chain_id.sync()

        max_priority_fee_per_gas = max_priority_fee_per_gas or Block.priority_fee().sync
        base_fee_per_gas = Block.pending().sync.base_fee_per_gas
        assert base_fee_per_gas, "block is earlier than London Hard Fork"
        max_fee_per_gas = max_fee_per_gas or (
            2 * base_fee_per_gas + max_priority_fee_per_gas
        )

        return PreparedTransaction(
            data=data,
            to=to,
            gas=HexInteger(gas),
            max_fee_per_gas=max_fee_per_gas,
            max_priority_fee_per_gas=max_priority_fee_per_gas,
            nonce=nonce or self.get_nonce().sync,
            value=value,
            access_list=access_list,
            chain_id=chain_id,
        )

    def estimate_gas(
        self,
        to: HexAddress,
        block_number: HexInteger | Literal["latest", "pending"] = "latest",
        data: HexStr = HexStr("0x"),
    ) -> RPCResponseModel[CallWithBlockArgs, HexInteger]:
        return RPCResponseModel(
            self._rpc().estimate_gas,
            CallWithBlockArgs(
                params=EthCallParams(
                    from_=self.address,
                    to=to,
                    data=data,
                ),
                block_number=block_number,
            ),
        )
