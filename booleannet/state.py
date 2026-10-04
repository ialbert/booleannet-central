"""
Classes to represent state of the simulation
"""
from itertools import *

class State(object):
    """
    Represents a state

    >>> state = State( b=0, c=1)
    >>> state.a = 1
    >>> state
    State: a=1, b=0, c=1
    >>> state.fp()
    0
    >>> state.bin()
    '101'
    """
    MAPPER, COUNTER  = {}, 0

    def __init__(self, **kwds ):
        self.__dict__.update( kwds )
    
    def __getitem__(self, key):
        return self.__dict__[key]
    
    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __repr__(self):  
        "Default string format"
        items = [ '%s=%s' % x for x in list(self.items()) ]
        items = ', '.join(items)
        return 'State: %s' % items
   
    def items(self):
        "Returns the sorted keys"
        return sorted( self.__dict__.items() )

    def keys(self):
        "Returns the sorted keys"
        return [ x for x,y in list(self.items()) ]

    def values(self):
        "Returns the values by sorted keys"
        return [ y for x,y in list(self.items()) ]

    def __iter__(self):
        return iter( list(self.keys()) )

    def copy(self):            
        "Duplicates itself"
        s = State( **self.__dict__ )
        return s

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def fp(self):
        "Returns a unique user friendly state definition"
        
        value = hash( str(self) )
        
        if value not in State.MAPPER:
            State.MAPPER[value] = State.COUNTER
            State.COUNTER += 1

        return State.MAPPER[value]
    
    def bin( self ):
        "A binary representation of the states"
        values = list(map(str, list(map(int, list(self.values())))))
        return ''.join(values)

def bit2int(bits):
    """
    Returns the integer corresponding of a bit state. 
    """
    value = 0
    for p, c in enumerate( reversed(bits) ):
        value += c * 2 ** p
    return value

def int2bit(x, w=20):
    """
    Generates a binary representation of an integer number (as a tuple)
    
    >>> bits = int2bit(10, w=4)
    >>> bits
    (1, 0, 1, 0)
    >>> bit2int( bits )
    10
    """
    bits = [ ]
    while x:
        bits.append(x%2)
        x /= 2
    
    # a bit of padding
    bits = bits + [ 0 ] * w
    bits = bits[:w]
    bits.reverse()
    return tuple(bits)

def all_initial_states( nodes, limit=None ):
    """
    Returns a generator that produces functions 
    can be used to initialize states.
    
    On each call to the lookup generator a different initial state 
    initializer will be produced

    >>> nodes = "A B".split()
    >>> generator = all_initial_states(nodes)
    >>>
    >>> for data, func in generator:
    ...     list(map(func, nodes))
    [False, False]
    [False, True]
    [True, False]
    [True, True]
    """
    def generator( nodes ):
        nodes = list(sorted(nodes))
        size  = len(nodes)
        for index in range( 2 ** size ):
            bits  = int2bit(index, w=size )
            bools = list(map(bool, bits))
            store = dict( list(zip(nodes, bools)) )
            def lookup( node ):
                return store[node]
            yield store, lookup
    
    return islice( generator(nodes), limit)
    
def test():
    """
    Main testrunnner
    """
    # runs the local suite
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()
    nodes = "A B C".split()
    gen = all_initial_states(nodes)

    for data, func in gen:
        print(list(map(func, nodes)))

