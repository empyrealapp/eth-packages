from sol_rpc.utils import CamelModel


class GetTransactionCountParams(CamelModel):
    commitment: str | None = None
    min_context_slot: int | None = None
