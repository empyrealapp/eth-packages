from typing import Literal

from eth_typing import HexAddress
from pydantic import BaseModel


class GMXEnvironment(BaseModel):
    chain: Literal["arbitrum", "avalanche"]
    datastore: HexAddress
    event_emitter: HexAddress
    exchange_router: HexAddress
    deposit_vault: HexAddress
    withdrawal_vault: HexAddress
    order_vault: HexAddress
    synthetics_reader: HexAddress
    synthetics_router: HexAddress
    glv_reader: HexAddress

    tokens_url: str

    @classmethod
    def get_environment(cls, network: Literal["arbitrum", "avalanche"]) -> "GMXEnvironment":
        if network == "arbitrum":
            return GMXArbitrum
        elif network == "avalanche":
            return GMXAvalanche
        else:
            raise ValueError(f"Invalid network: {network}")


GMXArbitrum = GMXEnvironment(
    chain="arbitrum",
    datastore="0xFD70de6b91282D8017aA4E741e9Ae325CAb992d8",
    event_emitter="0xC8ee91A54287DB53897056e12D9819156D3822Fb",
    exchange_router="0x69C527fC77291722b52649E45c838e41be8Bf5d5",
    deposit_vault="0xF89e77e8Dc11691C9e8757e84aaFbCD8A67d7A55",
    withdrawal_vault="0x0628D46b5D145f183AdB6Ef1f2c97eD1C4701C55",
    order_vault="0x31eF83a530Fde1B38EE9A18093A333D8Bbbc40D5",
    synthetics_reader="0x5Ca84c34a381434786738735265b9f3FD814b824",
    synthetics_router="0x7452c558d45f8afC8c83dAe62C3f8A5BE19c71f6",
    glv_reader="0xd4f522c4339Ae0A90a156bd716715547e44Bed65",
    tokens_url="https://arbitrum-api.gmxinfra.io/tokens",
)

GMXAvalanche = GMXEnvironment(
    chain="avalanche",
    datastore="0x2F0b22339414ADeD7D5F06f9D604c7fF5b2fe3f6",
    event_emitter="0xDb17B211c34240B014ab6d61d4A31FA0C0e20c26",
    exchange_router="0x3BE24AED1a4CcaDebF2956e02C27a00726D4327d",
    deposit_vault="0x90c670825d0C62ede1c5ee9571d6d9a17A722DFF",
    withdrawal_vault="0xf5F30B10141E1F63FC11eD772931A8294a591996",
    order_vault="0xD3D60D22d415aD43b7e64b510D86A30f19B1B12C",
    synthetics_reader="0xBAD04dDcc5CC284A86493aFA75D2BEb970C72216",
    synthetics_router="0x820F5FfC5b525cD4d88Cd91aCf2c28F16530Cc68",
    glv_reader=None,
    tokens_url="https://avalanche-api.gmxinfra.io/tokens",
)
