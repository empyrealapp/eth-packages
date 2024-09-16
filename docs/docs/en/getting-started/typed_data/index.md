# EIP712

## Hashing Typed Data

EIP712 is a protocol for standardizing the signing of typed data. This is useful for contracts where you might need to verify an offchain signature onchain. The digest that is signed consists of two parts: the domain and the message. The message is also sometimes referred to as the struct or the payload.

In order to buid the typed data, you need to use the `EIP712Model`, which inherits from the `Struct` model but adds additional capabilities.  You are able to build your typed data like this example:

```python
from eth_rpc.types import EIP712Model, hash_eip712_bytes

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
hashed_mail = hash_eip712_bytes(domain, mail)
```

---

## Signing the Hashed Data

If you need to sign this hashed data, you can easily do it with the `PrivateKeyWallet` class:

```python
from eth_rpc import PrivateKeyWallet

wallet = PrivateKeyWallet(pvt_hex="0x...")
signed_msg = wallet.sign_hash(hashed_mail)
```
