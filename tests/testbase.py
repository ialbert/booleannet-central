"""
Common functionality to all tests runners
"""
import sys, unittest

# path fixup to insert the most current path when developing
sys.path.insert(0, '..' )

import booleannet

#
# helper functions
#
def join( data, sep='\n', patt='%s'):
    return patt % sep.join( map(str, data) )

get     = lambda elem, attr: getattr(elem, attr)        
istrue  = lambda x: x 
isfalse = lambda x: not x 

def get_states( mode, text, steps, missing=None):
    """
    Helper function that generates the states based on 
    """
    model  = booleannet.Model( mode=mode, text=text )
    model.initialize( missing=missing )
    model.iterate( steps=steps )
    return model.states

class TestBase( unittest.TestCase ):

    def setUp(self):
        self.EQ = self.assertEqual

def test():
    pass

if __name__ == '__main__':
    test()