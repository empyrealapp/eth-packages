import time
from collections import OrderedDict
from threading import RLock
from typing import Generic, TypeVar, Union

T = TypeVar("T")
U = TypeVar("U")


class ExpiringDict(OrderedDict[T, U], Generic[T, U]):
    def __init__(
        self, max_len: Union[int, None], max_age_seconds: Union[float, None], items=None
    ):
        if not self.__is_instance_of_expiring_dict(items):
            self.__assertions(max_len, max_age_seconds)

        OrderedDict.__init__(self)  # type: ignore
        self.max_len = max_len
        self.max_age = max_age_seconds
        self.lock = RLock()
        self._safe_keys = lambda: list(self.keys())

        if items is not None:
            if self.__is_instance_of_expiring_dict(items):
                self.__copy_expiring_dict(max_len, max_age_seconds, items)
            elif self.__is_instance_of_dict(items):
                self.__copy_dict(items)
            elif self.__is_reduced_result(items):
                self.__copy_reduced_result(items)

            else:
                raise ValueError("can not unpack items")

    def __contains__(self, key):
        """Return True if the dict has a key, else return False."""
        try:
            with self.lock:
                item = OrderedDict.__getitem__(self, key)
                if time.time() - item[1] < self.max_age:
                    return True
                else:
                    del self[key]
        except KeyError:
            pass
        return False

    def __getitem__(self, key) -> U:
        """Return the item of the dict.

        Raises a KeyError if key is not in the map.
        """
        with self.lock:
            item = OrderedDict.__getitem__(self, key)  # type: ignore
            item_age = time.time() - item[1]  # type: ignore
            if item_age < self.max_age:
                return item[0]  # type: ignore
            else:
                del self[key]
                raise KeyError(key)

    def __setitem__(self, key, value, set_time=None):
        """Set d[key] to value."""
        with self.lock:
            if len(self) == self.max_len:
                if key in self:
                    del self[key]
                else:
                    try:
                        self.popitem(last=False)
                    except KeyError:
                        pass
            if set_time is None:
                set_time = time.time()
            OrderedDict.__setitem__(self, key, (value, set_time))

    def pop(self, key, default=None):
        """Get item from the dict and remove it.

        Return default if expired or does not exist. Never raise KeyError.
        """
        with self.lock:
            try:
                item = OrderedDict.__getitem__(self, key)
                del self[key]
                return item[0]
            except KeyError:
                return default

    def ttl(self, key):
        """Return TTL of the `key` (in seconds).

        Returns None for non-existent or expired keys.
        """
        key_value, key_age = self.get(key, with_age=True)
        if key_age:
            key_ttl = self.max_age - key_age
            if key_ttl > 0:
                return key_ttl
        return None

    def get(self, key, default=None, with_age=False):
        """Return the value for key if key is in the dictionary, else default."""
        try:
            return self.__getitem__(key, with_age)
        except KeyError:
            if with_age:
                return default, None
            else:
                return default

    def items(self):
        """Return a copy of the dictionary's list of (key, value) pairs."""
        r = []
        for key in self._safe_keys():
            try:
                r.append((key, self[key]))
            except KeyError:
                pass
        return r

    def items_with_timestamp(self):
        """Return a copy of the dictionary's list of (key, value, timestamp) triples."""
        r = []
        for key in self._safe_keys():
            try:
                r.append((key, OrderedDict.__getitem__(self, key)))
            except KeyError:
                pass
        return r

    def values(self):
        """Return a copy of the dictionary's list of values.
        See the note for dict.items()."""
        r = []
        for key in self._safe_keys():
            try:
                r.append(self[key])
            except KeyError:
                pass
        return r

    def fromkeys(self):
        """Create a new dictionary with keys from seq and values set to value."""
        raise NotImplementedError()

    def iteritems(self):
        """Return an iterator over the dictionary's (key, value) pairs."""
        raise NotImplementedError()

    def itervalues(self):
        """Return an iterator over the dictionary's values."""
        raise NotImplementedError()

    def viewitems(self):
        """Return a new view of the dictionary's items ((key, value) pairs)."""
        raise NotImplementedError()

    def viewkeys(self):
        """Return a new view of the dictionary's keys."""
        raise NotImplementedError()

    def viewvalues(self):
        """Return a new view of the dictionary's values."""
        raise NotImplementedError()

    def __reduce__(self):
        reduced = (
            self.__class__,
            (
                self.max_len,
                self.max_age,
                ("reduce_result", self.items_with_timestamp()),
            ),
        )
        return reduced

    def __assertions(self, max_len, max_age_seconds):
        self.__assert_max_len(max_len)
        self.__assert_max_age_seconds(max_age_seconds)

    @staticmethod
    def __assert_max_len(max_len):
        assert max_len >= 1

    @staticmethod
    def __assert_max_age_seconds(max_age_seconds):
        assert max_age_seconds >= 0

    @staticmethod
    def __is_reduced_result(items):
        if len(items) == 2 and items[0] == "reduce_result":
            return True
        return False

    @staticmethod
    def __is_instance_of_expiring_dict(items):
        if items is not None:
            if isinstance(items, ExpiringDict):
                return True
        return False

    @staticmethod
    def __is_instance_of_dict(items):
        if isinstance(items, dict):
            return True
        return False

    @property
    def size(self):
        return len(self.keys())

    def __copy_expiring_dict(
        self, max_len: Union[int, None], max_age_seconds: Union[float, None], items
    ):
        if max_len is not None:
            self.__assert_max_len(max_len)
            self.max_len = max_len
        else:
            self.max_len = items.max_len

        if max_age_seconds is not None:
            self.__assert_max_age_seconds(max_age_seconds)
            self.max_age = max_age_seconds
        else:
            self.max_age = items.max_age

        [
            self.__setitem__(key, value, set_time)
            for key, (value, set_time) in items.items_with_timestamp()
        ]

    def __copy_dict(self, items):
        [self.__setitem__(key, value) for key, value in items.items()]

    def __copy_reduced_result(self, items):
        [self.__setitem__(key, value, set_time) for key, (value, set_time) in items[1]]
