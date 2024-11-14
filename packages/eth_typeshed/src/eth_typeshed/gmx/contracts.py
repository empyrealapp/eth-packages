from pydantic import BaseModel

from eth_rpc import ProtocolBase
from eth_rpc.networks import get_network_by_name

from .datastore import Datastore
from .event_emitter import EventEmitter
from .exchange_router import ExchangeRouter
from .deposit_vault import DepositVault
from .withdrawal_vault import WithdrawalVault
from .order_vault import OrderVault
from .synthetics_reader.synthetics_reader import SyntheticsReader
from .synthetics_router import SyntheticsRouter
from .glv_reader import GLVReader


class GMXContract(BaseModel):
    contract: type[ProtocolBase]
    networks: dict[str, str | None]

    def get_instance(self, network: str) -> "ProtocolBase":
        network_type = get_network_by_name(network)
        if network not in self.networks:
            raise ValueError(f"Contract not found for network: {network}")

        contract_address = self.networks[network]
        contract = self.contract[network_type](address=contract_address)
        return contract


CONTRACTS = {
    "datastore": GMXContract(
        networks={
            "arbitrum": "0xFD70de6b91282D8017aA4E741e9Ae325CAb992d8",
            "avalanche": "0x2F0b22339414ADeD7D5F06f9D604c7fF5b2fe3f6"
        },
        contract=Datastore
    ),
    "eventemitter": GMXContract(
        networks={
            "arbitrum": "0xC8ee91A54287DB53897056e12D9819156D3822Fb",
            "avalanche": "0xDb17B211c34240B014ab6d61d4A31FA0C0e20c26"
        },
        contract=EventEmitter
    ),
    "exchangerouter": GMXContract(
        networks={
            "arbitrum": "0x69C527fC77291722b52649E45c838e41be8Bf5d5",
            "avalanche": "0x3BE24AED1a4CcaDebF2956e02C27a00726D4327d"
        },
        contract=ExchangeRouter
    ),
    "depositvault": GMXContract(
        networks={
            "arbitrum": "0xF89e77e8Dc11691C9e8757e84aaFbCD8A67d7A55",
            "avalanche": "0x90c670825d0C62ede1c5ee9571d6d9a17A722DFF"
        },
        contract=DepositVault
    ),
    "withdrawalvault": GMXContract(
        networks={
            "arbitrum": "0x0628D46b5D145f183AdB6Ef1f2c97eD1C4701C55",
            "avalanche": "0xf5F30B10141E1F63FC11eD772931A8294a591996"
        },
        contract=WithdrawalVault
    ),
    "ordervault": GMXContract(
        networks={
            "arbitrum": "0x31eF83a530Fde1B38EE9A18093A333D8Bbbc40D5",
            "avalanche": "0xD3D60D22d415aD43b7e64b510D86A30f19B1B12C"
        },
        contract=OrderVault
    ),
    "syntheticsreader": GMXContract(
        networks={
            "arbitrum": "0x5Ca84c34a381434786738735265b9f3FD814b824",
            "avalanche": "0xBAD04dDcc5CC284A86493aFA75D2BEb970C72216"
        },
        contract=SyntheticsReader
    ),
    "syntheticsrouter": GMXContract(
        networks={
            "arbitrum": "0x7452c558d45f8afC8c83dAe62C3f8A5BE19c71f6",
            "avalanche": "0x820F5FfC5b525cD4d88Cd91aCf2c28F16530Cc68"
        },
        contract=SyntheticsRouter
    ),
    "glvreader": GMXContract(
        networks={
            "arbitrum": "0xd4f522c4339Ae0A90a156bd716715547e44Bed65",
            "avalanche": None
        },
        contract=GLVReader
    )
}
