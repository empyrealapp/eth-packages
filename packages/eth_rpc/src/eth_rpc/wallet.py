import secrets
from abc import ABC, abstractmethod
from typing import Any, Literal, Optional

from eth_account import Account as EthAccount
from eth_account.account import LocalAccount, SignedMessage
from eth_rpc.types import (
    BLOCK_STRINGS,
    CallWithBlockArgs,
    EthCallParams,
    GetAccountArgs,
    RawTransaction,
    SignedTransaction,
)
from eth_typing import HexAddress, HexStr
from pydantic import ConfigDict, PrivateAttr

from ._request import Request
from ._transport import _force_get_global_rpc
from .account import Account
from .block import Block
from .transaction import PreparedTransaction
from .types import HexInteger, RPCResponseModel


class BaseWallet(Request, ABC):
    @property
    @abstractmethod
    def address(self) -> HexAddress: ...

    def get_nonce(self, block_number: int | BLOCK_STRINGS = "latest"):
        return RPCResponseModel(
            self.rpc().get_tx_count,
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
    _address: HexAddress = PrivateAttr()

    @property
    def address(self) -> HexAddress:
        return self._address

    def sign_transaction(self, tx):
        raise NotImplementedError("Mock wallet can not sign")


class PrivateKeyWallet(BaseWallet):
    private_key: HexStr
    _account: LocalAccount = PrivateAttr()

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def model_post_init(self, __context: Any) -> None:
        self._account = EthAccount.from_key(self.private_key)
        return super().model_post_init(__context)

    @property
    def address(self) -> HexAddress:
        return self._account.address

    @staticmethod
    def get_pvt_key() -> HexStr:
        priv = secrets.token_hex(32)
        return HexStr(f"0x{priv}")

    @classmethod
    def create_new(cls):
        return cls(private_key=cls.get_pvt_key())

    def sign_transaction(self, tx: PreparedTransaction) -> SignedTransaction:
        signed_tx = self._account.sign_transaction(tx.model_dump())
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
            self.rpc().send_raw_tx,
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
            self.rpc().estimate_gas,
            CallWithBlockArgs(
                params=EthCallParams(
                    from_=self.address,
                    to=to,
                    data=data,
                ),
                block_number=block_number,
            ),
        )

    def transfer(
        self, to: HexAddress, value: int
    ) -> RPCResponseModel[RawTransaction, HexStr]:
        prepared_tx = self.prepare(to=to, value=value)
        signed_tx = self.sign_transaction(prepared_tx)
        return self.send_raw_transaction(HexStr("0x" + signed_tx.raw_transaction))

    def sign_hash(self, hashed: bytes) -> SignedMessage:
        return EthAccount._sign_hash(hashed, self._account.key)  # type: ignore

    async def balance(self, block_number: int | BLOCK_STRINGS = "latest") -> int:
        return await Account.get_balance(self.address, block_number=block_number)

    @staticmethod
    def rsv_to_signature(r: int, s: int, v: int) -> HexStr:
        rr = hex(r)[2:].zfill(64)
        ss = hex(s)[2:].zfill(64)
        vv = hex(v)[2:]
        return HexStr("0x" + rr + ss + vv)

    @staticmethod
    def signature_to_rsv(signature: HexStr) -> tuple[int, int, int]:
        v = signature[-2:]
        s = signature[-66:-2]
        r = signature[:-66].lstrip("0x")

        return int(r, 16), int(s, 16), int(v, 16)
