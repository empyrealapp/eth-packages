from typing import Annotated

from eth_typing import HexAddress
from pydantic import BeforeValidator

from eth_rpc.utils import to_checksum


ChecksumAddress = Annotated[HexAddress, BeforeValidator(lambda x, info: to_checksum(x))]
