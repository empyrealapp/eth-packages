from typing import NewType, TypeVar, Union


# unsigned integers
u8 = NewType("u8", int)
u16 = NewType("u16", int)
u32 = NewType("u32", int)
u64 = NewType("u64", int)
u128 = NewType("u128", int)

# signed integers
i8 = NewType("i8", int)
i16 = NewType("i16", int)
i32 = NewType("i32", int)
i64 = NewType("i64", int)
i128 = NewType("i128", int)

# floating point numbers
f32 = NewType("f32", float)
f64 = NewType("f64", float)


PrimitiveArgType = TypeVar(
    "PrimitiveArgType",
    bound=Union[u8, u16, u32, u64, u128, i8, i16, i32, i64, i128, f32, f64],
)
