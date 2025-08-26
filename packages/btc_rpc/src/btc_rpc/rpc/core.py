import inspect
from typing import ClassVar

from pydantic import Field
from eth_typing import HexStr

from btc_rpc.types import (
    GetBlockHashRequest,
    GetBlockRequest,
    GetTxRequest,
    NoArgs,
    RawTransactionRequest,
    ChainInfo,
)
from .base import BaseRPC
from .method import RPCMethod
from btc_rpc.block import Block
from btc_rpc.transaction import Transaction


class RPC(BaseRPC):
    decode_raw_transaction: ClassVar = RPCMethod[RawTransactionRequest, Transaction](name="decoderawtransaction")
    get_best_hash: ClassVar = RPCMethod[NoArgs, HexStr](name="getbestblockhash")
    get_chain_info: ClassVar = RPCMethod[NoArgs, ChainInfo](name="getblockchaininfo")
    get_block_hash: ClassVar = RPCMethod[GetBlockHashRequest, HexStr](name="getblockhash")
    get_block: ClassVar = RPCMethod[GetBlockRequest, Block | HexStr](name="getblock")
    get_raw_transaction: ClassVar = RPCMethod[GetTxRequest, Transaction | HexStr](name="getrawtransaction")

    methods: dict[str, RPCMethod] = Field(default_factory=dict)

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
        rpc_methods = inspect.getmembers(self, predicate=lambda x: isinstance(x, RPCMethod))
        for name, method in rpc_methods:
            new_method = method.copy()
            self.methods[name] = new_method.set_rpc(self)
