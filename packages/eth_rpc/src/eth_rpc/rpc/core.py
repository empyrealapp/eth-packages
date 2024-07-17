import inspect
from typing import Any, ClassVar

from eth_rpc.block import Block
from eth_rpc.models import (
    AccessListResponse,
    Account,
    FeeHistory,
    Log,
    PendingTransaction,
)
from eth_rpc.transaction import AlchemyReceiptsResponse, Transaction, TransactionReceipt
from eth_rpc.types import (
    AlchemyBlockReceipt,
    BlockNumberArg,
    CallWithBlockArgs,
    Empty,
    EthCallArgs,
    FeeHistoryArgs,
    GetAccountArgs,
    GetBlockByHashArgs,
    GetBlockByNumberArgs,
    GetCodeArgs,
    GetStorageArgs,
    GetTransactionByBlockHash,
    GetTransactionByBlockNumber,
    HexInteger,
    LogsArgs,
    RawTransaction,
    TraceArgs,
    TransactionRequest,
)
from eth_typing import HexStr
from pydantic import Field

from .base import BaseRPC
from .method import RPCMethod


class RPC(BaseRPC):
    chain_id: ClassVar = RPCMethod[Empty, HexInteger](name="eth_chainId")
    max_priority_fee_per_gas: ClassVar = RPCMethod[Empty, HexInteger](
        name="eth_maxPriorityFeePerGas"
    )
    fee_history: ClassVar = RPCMethod[FeeHistoryArgs, FeeHistory](name="eth_feeHistory")
    eth_call: ClassVar = RPCMethod[EthCallArgs, HexStr](name="eth_call")
    get_block_by_hash: ClassVar = RPCMethod[GetBlockByHashArgs, Block](
        name="eth_getBlockByHash"
    )
    get_block_by_number: ClassVar = RPCMethod[GetBlockByNumberArgs, Block](
        name="eth_getBlockByNumber"
    )
    get_block_tx_count_by_number: ClassVar = RPCMethod[BlockNumberArg, HexInteger](
        name="eth_getBlockTransactionCountByNumber",
    )
    get_tx_by_hash: ClassVar = RPCMethod[TransactionRequest, Transaction | None](
        name="eth_getTransactionByHash"
    )
    get_pending_tx_by_hash: ClassVar = RPCMethod[
        TransactionRequest, PendingTransaction | None
    ](name="eth_getTransactionByHash")
    estimate_gas: ClassVar = RPCMethod[CallWithBlockArgs, HexInteger](
        name="eth_estimateGas"
    )
    block_number: ClassVar = RPCMethod[Empty, HexInteger](name="eth_blockNumber")
    create_access_list: ClassVar = RPCMethod[CallWithBlockArgs, AccessListResponse](
        name="eth_createAccessList"
    )
    get_storage_at: ClassVar = RPCMethod[GetStorageArgs, HexStr](
        name="eth_getStorageAt"
    )
    get_code: ClassVar = RPCMethod[GetCodeArgs, HexStr](name="eth_getCode")
    get_tx_receipt: ClassVar = RPCMethod[TransactionRequest, TransactionReceipt | None](
        name="eth_getTransactionReceipt"
    )
    get_block_receipts: ClassVar = RPCMethod[
        list[HexInteger | HexStr], list[TransactionReceipt]
    ](name="eth_getBlockReceipts")
    alchemy_get_block_receipts: ClassVar = RPCMethod[
        AlchemyBlockReceipt, AlchemyReceiptsResponse
    ](name="alchemy_getTransactionReceipts")
    get_tx_by_block_hash: ClassVar = RPCMethod[GetTransactionByBlockHash, Transaction](
        name="eth_getTransactionByBlockHashAndIndex"
    )
    get_tx_by_block_number: ClassVar = RPCMethod[
        GetTransactionByBlockNumber, Transaction
    ](name="eth_getTransactionByBlockNumberAndIndex")
    get_balance: ClassVar = RPCMethod[GetAccountArgs, HexInteger](name="eth_getBalance")
    get_account: ClassVar = RPCMethod[GetAccountArgs, Account](name="eth_getAccount")
    get_tx_count: ClassVar = RPCMethod[GetAccountArgs, HexInteger](
        name="eth_getTransactionCount"
    )
    get_logs: ClassVar = RPCMethod[LogsArgs, list[Log]](name="eth_getLogs")

    send_raw_tx: ClassVar = RPCMethod[RawTransaction, HexStr](
        name="eth_sendRawTransaction"
    )

    methods: dict[str, RPCMethod] = Field(default_factory=dict)

    # debug methods
    debug_tracecall: ClassVar = RPCMethod[TraceArgs, Any](name="debug_traceCall")

    def __getattribute__(self, name):
        """
        This makes it so you can assign copies of the RPCMethod ClassVars to the instance.
        Otherwise, all RPC instances would share the same method classes, and this would
        make it difficult to have method calls on different networks.
        """
        dict_ = super().__getattribute__("__dict__")
        methods = dict_.get("methods", {})
        if name in methods:
            return methods[name]
        return super().__getattribute__(name)

    def model_post_init(self, __context):
        rpc_methods = inspect.getmembers(
            self, predicate=lambda x: isinstance(x, RPCMethod)
        )
        for name, method in rpc_methods:
            new_method = method.copy()
            self.methods[name] = new_method.set_rpc(self).set_network(self.network)
