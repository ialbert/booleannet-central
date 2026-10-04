#
# a dictionary-like class that maintains the order of insertion
# 
# based on a recipe by Igor Ghisi located at
#
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496761
#
from collections.abc import MutableMapping as DictMixin

class odict(DictMixin):
    """
    >>> o = odict()
    >>> o[2]=20 ; o[1]=10
    >>> o.keys()
    [2, 1]
    >>> o.values()
    [20, 10]
    >>> o.items()
    [(2, 20), (1, 10)]
    >>> [ x for x in o ]
    [2, 1]

    """
    def __init__(self, **kwds):
        self._keys = []
        self._data = {}
        for key, value in list(kwds.items()):
            self[key] = value
        
    def __setitem__(self, key, value):
        if key not in self._data:
            self._keys.append(key)
        self._data[key] = value
        
    def __getitem__(self, key):
        return self._data[key]
    
    def __delitem__(self, key):
        del self._data[key]
        self._keys.remove(key)

    def __iter__(self):
        return iter(self._keys)

    def __len__(self):
        return len(self._keys)

    def keys(self):
        return list(self._keys)

    def values(self):
        return [self._data[key] for key in self._keys]

    def items(self):
        return [(key, self._data[key]) for key in self._keys]
    
    def copy(self):
        copyDict = odict()
        copyDict._data = self._data.copy()
        copyDict._keys = self._keys[:]
        return copyDict

if __name__ == '__main__':
    import doctest
    doctest.testmod()