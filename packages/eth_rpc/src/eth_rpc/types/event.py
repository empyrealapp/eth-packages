from dataclasses import dataclass


class Indexed:
    pass


@dataclass(eq=True, frozen=True)
class Name:
    value: str
