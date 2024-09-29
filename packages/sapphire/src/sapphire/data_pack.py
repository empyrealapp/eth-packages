import cbor2
from eth_account.account import Account, LocalAccount
from eth_rpc import Block, PrivateKeyWallet
from eth_rpc.types import primitives
from eth_typing import HexStr
from pydantic import BaseModel, Field

TYPES = {
    "Call": [
        {"name": "from", "type": "address"},
        {"name": "to", "type": "address"},
        {"name": "gasLimit", "type": "uint64"},
        {"name": "gasPrice", "type": "uint256"},
        {"name": "value", "type": "uint256"},
        {"name": "data", "type": "bytes"},
        {"name": "leash", "type": "Leash"},
    ],
    "Leash": [
        {"name": "nonce", "type": "uint64"},
        {"name": "blockNumber", "type": "uint64"},
        {"name": "blockHash", "type": "bytes32"},
        {"name": "blockRange", "type": "uint64"},
    ],
}


def make_upgraded_domain(chain_id: int):
    return {
        "name": "oasis-runtime-sdk/evm: signed query",
        "version": "1.0.0",
        "chainId": hex(chain_id),
    }


def make_upgraded_call(
    from_,
    to,
    data,
    block_number,
    block_hash,
    nonce,
    gas_limit: int = 30000000,
    gas_price: str = "01",
    value: str = "0x0",
    block_range: int = 4000,
):
    return {
        "from": from_,
        "to": to,
        "gasLimit": gas_limit,
        "gasPrice": gas_price,
        "value": value,
        "data": data,
        "leash": {
            "nonce": nonce,
            "blockNumber": block_number,
            "blockHash": block_hash,
            "blockRange": block_range,
        },
    }


def sign(
    domain,
    call,
    acc: LocalAccount,
    types: dict = TYPES,
):
    return Account.sign_typed_data(
        acc.key,
        domain,
        types,
        call,
    )


def make_body(
    nonce, signature, envelope, block_hash, block_number, block_range: int = 4000
):
    body = {
        "data": {
            "body": {
                "pk": envelope["body"]["pk"],
                "data": envelope["body"]["data"],
                "epoch": envelope["body"]["epoch"],
                "nonce": envelope["body"]["nonce"],
            },
            "format": 1,
        },
        "leash": {
            "nonce": nonce,
            "block_hash": block_hash,
            "block_range": block_range,
            "block_number": block_number,
        },
        "signature": signature,
    }
    return "0x" + cbor2.dumps(body).hex()


class SignedResponse(BaseModel):
    from_: primitives.address = Field(serialization_alias="from")
    to: primitives.address = Field(serialization_alias="to")
    data: HexStr

    def model_dump(self, *args, **kwargs):
        return {
            "from": self.from_,
            "to": self.to,
            "data": self.data,
        }


class SignedArgs(BaseModel):
    req: SignedResponse
    block: str = "latest"

    def model_dump(self):
        return {
            "req": self.req.model_dump(),
            "block": self.block,
        }


def make_response(
    from_,
    to,
    data,
    envelope,
    wallet: PrivateKeyWallet,
    chain_id: int = 0x5AFF,
):
    block: Block = Block.latest().sync  # type: ignore
    block_number = block.number - 1
    block = Block.load_by_number(block_number).sync  # type: ignore
    block_hash = bytes.fromhex(block.hash[2:])  # type: ignore
    nonce = wallet.get_nonce().sync + 15
    call = make_upgraded_call(from_, to, data, block_number, block_hash, nonce)
    domain = make_upgraded_domain(chain_id)
    data = Account.sign_typed_data(wallet.private_key, domain, TYPES, call)
    signature = data.signature

    return SignedResponse(
        from_=from_,
        to=to,
        data=make_body(nonce, signature, envelope, block_hash, block_number),
    )
