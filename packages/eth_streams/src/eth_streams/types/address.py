class Address(str):
    def __eq__(self, other: object):
        if not isinstance(other, str):
            raise ValueError("Can only compare str with str")
        return self.lower() == other.lower()
