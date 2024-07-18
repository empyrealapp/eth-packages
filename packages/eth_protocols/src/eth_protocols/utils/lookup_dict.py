from sortedcontainers import SortedDict


class LookupDict:
    def __init__(self):
        self.data = SortedDict()

    def add(self, key, value):
        self.data[key] = value

    def find_lte(self, key):
        # Find the closest key that is less than or equal to the given key
        idx = self.data.bisect_right(key) - 1
        if idx == -1:
            return None, None  # If all keys in the dict are greater than the given key
        closest_key = self.data.iloc[idx]
        return closest_key, self.data[closest_key]

    def find_gte(self, key):
        # Find the closest key that is equal to or larger than the given key
        idx = self.data.bisect_left(key)
        if idx == len(self.data):
            return None, None  # If all keys in the dict are smaller than the given key
        closest_key = self.data.iloc[idx]
        return closest_key, self.data[closest_key]

    def range_iterator(self, low_key, high_key):
        for key in self.data.irange(low_key, high_key, inclusive=(True, True)):
            yield key, self.data[key]
