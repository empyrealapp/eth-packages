from typing import NewType

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


bytes1 = NewType("bytes1", str)
bytes2 = NewType("bytes2", str)
bytes3 = NewType("bytes3", str)
bytes4 = NewType("bytes4", str)
bytes5 = NewType("bytes5", str)
bytes6 = NewType("bytes6", str)
bytes7 = NewType("bytes7", str)
bytes8 = NewType("bytes8", str)
bytes9 = NewType("bytes9", str)
bytes10 = NewType("bytes10", str)
bytes11 = NewType("bytes11", str)
bytes12 = NewType("bytes12", str)
bytes13 = NewType("bytes13", str)
bytes14 = NewType("bytes14", str)
bytes15 = NewType("bytes15", str)
bytes16 = NewType("bytes16", str)
bytes17 = NewType("bytes17", str)
bytes18 = NewType("bytes18", str)
bytes19 = NewType("bytes19", str)
bytes20 = NewType("bytes20", str)
bytes21 = NewType("bytes21", str)
bytes22 = NewType("bytes22", str)
bytes23 = NewType("bytes23", str)
bytes24 = NewType("bytes24", str)
bytes25 = NewType("bytes25", str)
bytes26 = NewType("bytes26", str)
bytes27 = NewType("bytes27", str)
bytes28 = NewType("bytes28", str)
bytes29 = NewType("bytes29", str)
bytes30 = NewType("bytes30", str)
bytes31 = NewType("bytes31", str)
bytes32 = NewType("bytes32", str)

string = NewType("string", str)
address = NewType("address", str)

# redundant, but facilitates code consistency, ie. tuple[primitives.bool, primitives.address]
bool = bool
bytes = bytes
