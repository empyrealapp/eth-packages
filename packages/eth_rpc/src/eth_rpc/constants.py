import asyncio
from contextvars import ContextVar

from eth_typing import HexAddress, HexStr

ADDRESS_ZERO = HexAddress(HexStr("0x0000000000000000000000000000000000000000"))
ADDRESS_DEAD = HexAddress(HexStr("0x000000000000000000000000000000000000dEaD"))

DEFAULT_EVENT = asyncio.Event()
DEFAULT_EVENT.set()
DEFAULT_CONTEXT = ContextVar[int]("DEFAULT_CONTEXT", default=0)
