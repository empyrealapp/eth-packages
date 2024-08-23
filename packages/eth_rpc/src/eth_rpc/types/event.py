from dataclasses import dataclass


class Indexed:
    """Used to annotate when an event field is indexed"""


@dataclass(eq=True, frozen=True)
class Name:
    """Used to annotate a name for variables different than its declared name"""

    value: str
