from eth_rpc.rpc import BaseRPC, RPCMethod
from eth_rpc.types import NoArgs
from sol_rpc.types.args.block import BlockArgs, Block
from sol_rpc.types.args.get_transaction_count import GetTransactionCountParams
from sol_rpc.types.args.get_version import GetVersionResponse
from sol_rpc.types.args.send_transaction import SendTransactionArgs


class RPC(BaseRPC):
    get_block: RPCMethod = RPCMethod[BlockArgs, Block](name="getBlock")
    send_transaction: RPCMethod = RPCMethod[SendTransactionArgs, str](name="sendTransaction")
    get_transaction_count: RPCMethod = RPCMethod[GetTransactionCountParams, int](name="getTransactionCount")
    get_version: RPCMethod = RPCMethod[NoArgs, GetVersionResponse](name="getVersion")

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
