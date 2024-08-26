from typing import NewType, Union

from eth_typing import ChecksumAddress, HexAddress, HexStr

int8 = NewType("int8", int)
int16 = NewType("int16", int)
int24 = NewType("int24", int)
int32 = NewType("int32", int)
int40 = NewType("int40", int)
int48 = NewType("int48", int)
int56 = NewType("int56", int)
int64 = NewType("int64", int)
int72 = NewType("int72", int)
int80 = NewType("int80", int)
int88 = NewType("int88", int)
int96 = NewType("int96", int)
int104 = NewType("int104", int)
int112 = NewType("int112", int)
int120 = NewType("int120", int)
int128 = NewType("int128", int)
int136 = NewType("int136", int)
int144 = NewType("int144", int)
int152 = NewType("int152", int)
int160 = NewType("int160", int)
int168 = NewType("int168", int)
int176 = NewType("int176", int)
int184 = NewType("int184", int)
int192 = NewType("int192", int)
int200 = NewType("int200", int)
int208 = NewType("int208", int)
int216 = NewType("int216", int)
int224 = NewType("int224", int)
int232 = NewType("int232", int)
int240 = NewType("int240", int)
int248 = NewType("int248", int)
int256 = NewType("int256", int)

uint8 = NewType("uint8", int)
uint16 = NewType("uint16", int)
uint24 = NewType("uint24", int)
uint32 = NewType("uint32", int)
uint40 = NewType("uint40", int)
uint48 = NewType("uint48", int)
uint56 = NewType("uint56", int)
uint64 = NewType("uint64", int)
uint72 = NewType("uint72", int)
uint80 = NewType("uint80", int)
uint88 = NewType("uint88", int)
uint96 = NewType("uint96", int)
uint104 = NewType("uint104", int)
uint112 = NewType("uint112", int)
uint120 = NewType("uint120", int)
uint128 = NewType("uint128", int)
uint136 = NewType("uint136", int)
uint144 = NewType("uint144", int)
uint152 = NewType("uint152", int)
uint160 = NewType("uint160", int)
uint168 = NewType("uint168", int)
uint176 = NewType("uint176", int)
uint184 = NewType("uint184", int)
uint192 = NewType("uint192", int)
uint200 = NewType("uint200", int)
uint208 = NewType("uint208", int)
uint216 = NewType("uint216", int)
uint224 = NewType("uint224", int)
uint232 = NewType("uint232", int)
uint240 = NewType("uint240", int)
uint248 = NewType("uint248", int)
uint256 = NewType("uint256", int)


bytes1 = NewType("bytes1", bytes)
bytes2 = NewType("bytes2", bytes)
bytes3 = NewType("bytes3", bytes)
bytes4 = NewType("bytes4", bytes)
bytes5 = NewType("bytes5", bytes)
bytes6 = NewType("bytes6", bytes)
bytes7 = NewType("bytes7", bytes)
bytes8 = NewType("bytes8", bytes)
bytes9 = NewType("bytes9", bytes)
bytes10 = NewType("bytes10", bytes)
bytes11 = NewType("bytes11", bytes)
bytes12 = NewType("bytes12", bytes)
bytes13 = NewType("bytes13", bytes)
bytes14 = NewType("bytes14", bytes)
bytes15 = NewType("bytes15", bytes)
bytes16 = NewType("bytes16", bytes)
bytes17 = NewType("bytes17", bytes)
bytes18 = NewType("bytes18", bytes)
bytes19 = NewType("bytes19", bytes)
bytes20 = NewType("bytes20", bytes)
bytes21 = NewType("bytes21", bytes)
bytes22 = NewType("bytes22", bytes)
bytes23 = NewType("bytes23", bytes)
bytes24 = NewType("bytes24", bytes)
bytes25 = NewType("bytes25", bytes)
bytes26 = NewType("bytes26", bytes)
bytes27 = NewType("bytes27", bytes)
bytes28 = NewType("bytes28", bytes)
bytes29 = NewType("bytes29", bytes)
bytes30 = NewType("bytes30", bytes)
bytes31 = NewType("bytes31", bytes)
bytes32 = NewType("bytes32", bytes)

string = NewType("string", str)
address = NewType("address", str)

# redundant, but facilitates code consistency, ie. tuple[primitives.bool, primitives.address]
bool = bool
bytes = bytes

BYTES_TYPES = Union[
    type[bytes1],
    type[bytes2],
    type[bytes3],
    type[bytes4],
    type[bytes5],
    type[bytes6],
    type[bytes7],
    type[bytes8],
    type[bytes9],
    type[bytes10],
    type[bytes11],
    type[bytes12],
    type[bytes13],
    type[bytes14],
    type[bytes15],
    type[bytes16],
    type[bytes17],
    type[bytes18],
    type[bytes19],
    type[bytes20],
    type[bytes21],
    type[bytes22],
    type[bytes23],
    type[bytes24],
    type[bytes25],
    type[bytes26],
    type[bytes27],
    type[bytes28],
    type[bytes29],
    type[bytes30],
    type[bytes31],
    type[bytes32],
    type[bytes],
]

BASIC_TYPES = Union[
    int8,
    int16,
    int24,
    int32,
    int40,
    int48,
    int56,
    int64,
    int72,
    int80,
    int88,
    int96,
    int104,
    int112,
    int120,
    int128,
    int136,
    int144,
    int152,
    int160,
    int168,
    int176,
    int184,
    int192,
    int200,
    int208,
    int216,
    int224,
    int232,
    int240,
    int248,
    int256,
    uint8,
    uint16,
    uint24,
    uint32,
    uint40,
    uint48,
    uint56,
    uint64,
    uint72,
    uint80,
    uint88,
    uint96,
    uint104,
    uint112,
    uint120,
    uint128,
    uint136,
    uint144,
    uint152,
    uint160,
    uint168,
    uint176,
    uint184,
    uint192,
    uint200,
    uint208,
    uint216,
    uint224,
    uint232,
    uint240,
    uint248,
    uint256,
    bytes1,
    bytes2,
    bytes3,
    bytes4,
    bytes5,
    bytes6,
    bytes7,
    bytes8,
    bytes9,
    bytes10,
    bytes11,
    bytes12,
    bytes13,
    bytes14,
    bytes15,
    bytes16,
    bytes17,
    bytes18,
    bytes19,
    bytes20,
    bytes21,
    bytes22,
    bytes23,
    bytes24,
    bytes25,
    bytes26,
    bytes27,
    bytes28,
    bytes29,
    bytes30,
    bytes31,
    bytes32,
    bytes,
    string,
    str,
    address,
    bool,
    HexAddress,
    ChecksumAddress,
    HexStr,
]

# in solidity, these can not be assigned to yet but can be declared
ufixed128x18 = NewType("ufixed128x18", float)
fixed128x18 = NewType("fixed128x18", float)
