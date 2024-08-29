from eth_rpc import PrivateKeyWallet
from eth_rpc.types import Domain, EIP712Model, hash_eip712_bytes, primitives
from eth_typing import HexStr
from pydantic import Field


class First(EIP712Model):
    x: int
    y: list[bool]


class Second(EIP712Model):
    first_: list[First] = Field(serialization_alias="first")
    second: tuple[bool, str]


def test_type_string():
    assert (
        Second.type_string()
        == b"Second(First[] first,(bool,string) second)First(uint256 x,bool[] y)"
    )


def test_domain_hash():
    domain = Domain(
        name="test",
        version="1",
        chain_id=1,
        verifying_contract="0x000000000000000000000000000000000000dead",
    )
    assert (
        domain.hash().hex()
        == "9304293a10b8d467c5e49bcf1cea604625f3771b366fee4aad461e904f7d9b8e"
    )

    assert (
        Second.type_string()
        == b"Second(First[] first,(bool,string) second)First(uint256 x,bool[] y)"
    )


def test_mail_example() -> None:
    # https://github.com/ethereum/EIPs/blob/master/assets/eip-712/Example.sol
    class Person(EIP712Model):
        name: str
        wallet: primitives.address

    class Mail(EIP712Model):
        from_: Person = Field(serialization_alias="from")
        to: Person
        contents: str

    mail = Mail(
        from_=Person(name="Cow", wallet="0xCD2a3d9F938E13CD947Ec05AbC7FE734Df8DD826"),
        to=Person(name="Bob", wallet="0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB"),
        contents="Hello, Bob!",
    )

    domain = Domain(
        name="Ether Mail",
        version="1",
        chain_id=1,
        verifying_contract="0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC",
    )
    assert (
        mail.type_string()
        == b"Mail(Person from,Person to,string contents)Person(string name,address wallet)"
    )
    assert domain.hash() == bytes.fromhex(
        "f2cee375fa42b42143804025fc449deafd50cc031ca257e0b194a650a912090f"
    )
    assert mail.hash() == bytes.fromhex(
        "c52c0ee5d84264471806290a3f2c4cecfc5490626bf912d01f240d7a274b371e"
    )

    hashed_mail = hash_eip712_bytes(domain, mail)

    v = 28
    r = HexStr("0x4355c47d63924e8a72e509b65029052eb6c299d53a04e167c5775fd466751c9d")
    s = HexStr("0x07299936d304c153f6443dfa05f40ff007d72911b6f72307f996231605b91562")
    assert EIP712Model.recover(hashed_mail, vrs=(v, r, s)) == mail.from_.wallet


def test_rvs():
    domain_hash = "9304293a10b8d467c5e49bcf1cea604625f3771b366fee4aad461e904f7d9b8e"
    wallet = PrivateKeyWallet(
        private_key="0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    )
    signature = wallet.sign_hash(domain_hash)
    assert (
        EIP712Model.recover(domain_hash, signature=signature.signature)
        == wallet.address
    )
    assert "0x" + signature.signature.hex() == wallet.rsv_to_signature(
        signature.r, signature.s, signature.v
    )
    wallet.signature_to_rsv(signature.signature.hex()) == (
        signature.r,
        signature.s,
        signature.v,
    )
