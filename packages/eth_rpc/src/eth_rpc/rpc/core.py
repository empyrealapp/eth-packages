from typing import Any

from eth_rpc.models import AccessListResponse, Account, FeeHistory, PendingTransaction
from eth_rpc.transaction import AlchemyReceiptsResponse
from eth_rpc.transaction import Transaction as TransactionModel
from eth_rpc.transaction import TransactionReceipt as TransactionReceiptModel
from eth_rpc.types import (
    AlchemyBlockReceipt,
    AlchemyTokenBalances,
    BlockNumberArg,
    CallWithBlockArgs,
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
    NoArgs,
    OasisCalldataPublicKey,
    RawTransaction,
    TraceArgs,
    TransactionRequest,
)
from eth_typing import HexAddress, HexStr

from ..block import Block
from ..log import Log
from .base import BaseRPC
from .method import RPCMethod


class RPC(BaseRPC):
    chain_id: RPCMethod = RPCMethod[NoArgs, HexInteger](name="eth_chainId")
    max_priority_fee_per_gas: RPCMethod = RPCMethod[NoArgs, HexInteger](
        name="eth_maxPriorityFeePerGas"
    )
    fee_history: RPCMethod = RPCMethod[FeeHistoryArgs, FeeHistory](
        name="eth_feeHistory"
    )
    eth_call: RPCMethod = RPCMethod[EthCallArgs, HexStr](name="eth_call")
    get_block_by_hash: RPCMethod = RPCMethod[GetBlockByHashArgs, Block](
        name="eth_getBlockByHash"
    )
    get_block_by_number: RPCMethod = RPCMethod[GetBlockByNumberArgs, Block](
        name="eth_getBlockByNumber"
    )
    get_block_tx_count_by_number: RPCMethod = RPCMethod[BlockNumberArg, HexInteger](
        name="eth_getBlockTransactionCountByNumber",
    )
    get_tx_by_hash: RPCMethod = RPCMethod[TransactionRequest, TransactionModel | None](
        name="eth_getTransactionByHash"
    )
    get_pending_tx_by_hash: RPCMethod = RPCMethod[
        TransactionRequest, PendingTransaction | None
    ](name="eth_getTransactionByHash")
    estimate_gas: RPCMethod = RPCMethod[CallWithBlockArgs, HexInteger](
        name="eth_estimateGas"
    )
    block_number: RPCMethod = RPCMethod[NoArgs, HexInteger](name="eth_blockNumber")
    create_access_list: RPCMethod = RPCMethod[CallWithBlockArgs, AccessListResponse](
        name="eth_createAccessList"
    )
    get_storage_at: RPCMethod = RPCMethod[GetStorageArgs, HexStr](
        name="eth_getStorageAt"
    )
    get_code: RPCMethod = RPCMethod[GetCodeArgs, HexStr](name="eth_getCode")
    get_tx_receipt: RPCMethod = RPCMethod[
        TransactionRequest, TransactionReceiptModel | None
    ](name="eth_getTransactionReceipt")
    get_block_receipts: RPCMethod = RPCMethod[
        list[HexInteger | HexStr], list[TransactionReceiptModel]
    ](name="eth_getBlockReceipts")
    get_tx_by_block_hash: RPCMethod = RPCMethod[
        GetTransactionByBlockHash, TransactionModel
    ](name="eth_getTransactionByBlockHashAndIndex")
    get_tx_by_block_number: RPCMethod = RPCMethod[
        GetTransactionByBlockNumber, TransactionModel
    ](name="eth_getTransactionByBlockNumberAndIndex")
    get_balance: RPCMethod = RPCMethod[GetAccountArgs, HexInteger](
        name="eth_getBalance"
    )
    get_account: RPCMethod = RPCMethod[GetAccountArgs, Account](name="eth_getAccount")
    get_tx_count: RPCMethod = RPCMethod[GetAccountArgs, HexInteger](
        name="eth_getTransactionCount"
    )
    get_logs: RPCMethod = RPCMethod[LogsArgs, list[Log]](name="eth_getLogs")

    send_raw_tx: RPCMethod = RPCMethod[RawTransaction, HexStr](
        name="eth_sendRawTransaction"
    )

    # oasis specific methods
    oasis_calldata_public_key: RPCMethod[NoArgs, OasisCalldataPublicKey] = RPCMethod[
        NoArgs, OasisCalldataPublicKey
    ](name="oasis_callDataPublicKey")

    # debug methods
    debug_tracecall: RPCMethod = RPCMethod[TraceArgs, Any](name="debug_traceCall")

    # alchemy
    alchemy_get_block_receipts: RPCMethod = RPCMethod[
        AlchemyBlockReceipt, AlchemyReceiptsResponse
    ](name="alchemy_getTransactionReceipts")
    alchemy_token_balances: RPCMethod = RPCMethod[
        list[HexAddress],
        AlchemyTokenBalances,
    ](name="alchemy_getTokenBalances")

    def model_post_init(self, __context):
        rpc_methods = []
        for method in dir(self):
            if method[0] == "_":
                continue
            try:
                attr = getattr(self, method)
                if isinstance(attr, RPCMethod):
                    rpc_methods.append((method, attr))
            except Exception:
                pass

        for name, method in rpc_methods:
            new_method = method.model_copy()
            setattr(self, name, new_method.set_rpc(self).set_network(self.network))

        return super().model_post_init(__context)
