from eth_rpc.types.typed_data import Domain, EIP712Model


class First(EIP712Model):
    x: int
    y: list[bool]


class Second(EIP712Model):
    first: First
    second: tuple[bool, str]


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

    assert Second.type_string() == b"Second(First first,(bool,string) second)"
