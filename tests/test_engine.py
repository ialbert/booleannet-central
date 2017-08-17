import sys, unittest, string
from random import randint, choice
from itertools import *

# import path fixup
sys.path.append( '..' )

import boolean
from boolean.functional import *

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
    Helper function to generate the states
    """
    eng  = boolean.Model( mode=mode, text=text )
    eng.initialize( missing=missing )
    eng.iterate( steps=steps )
    return eng.states
            
class EngineTest( unittest.TestCase ):
    
    def test_plde_engine( self ):
        "Testing PLDE"
        
        EQ = self.assertEqual

        text = """
        A = B = True
        C = False
        1: A* = A
        2: B* = A and B
        3: C* = not C
        """
        eng  = boolean.Model( mode='plde', text=text )
        eng.initialize()
        eng.iterate( fullt=1, steps=10 )
        EQ( len(eng.data), 3)
        EQ( len(eng.data['A']), 10)

    
    def test_initializer( self ):
        "Testing initializer"
        
        EQ = self.assertEqual

        text = """
        A = False
        1: A* = A
        2: B* = A and B
        3: C* = not C
        """
        eng  = boolean.Model( mode='sync', text=text )
        eng.initialize( missing= boolean.util.allfalse, defaults=dict(A=True, B=True) )
        eng.iterate( steps=10 )
        EQ( eng.start.A, True )
        EQ( eng.start.B, True )
        EQ( eng.start.C, False )
        EQ( len(eng.states), 11)

    def test_engine( self ):
        "Basic operation"
        
        EQ = self.assertEqual

        text = """
        A = B = True
        C = False
        1: A* = A
        2: B* = A and B
        3: C* = not C
        """
        eng  = boolean.Model( mode='sync', text=text )
        eng.initialize()
        eng.iterate( steps=5 )
        
        EQ( eng.start.A, True )
        EQ( eng.start.B, True )
        EQ( eng.start.C, False )

        EQ( eng.last.A, True )
        EQ( eng.last.B, True )
        EQ( eng.last.C, True )

    def test_eninge_modes( self ):
        "Testing engine modes"

        EQ = self.assertEqual

        text = """
        A = B = True
        C = False
        1: A* = A
        2: B* = A and B
        3: C* = not C
        """

        for mode in ( 'sync', 'async' ):
            
            states = get_states(mode=mode, text=text, steps=5)
            
            for state in states:
                EQ( state.A, True )

            # create extractor functions
            funcs  = [ partial( get, attr=attr ) for attr in 'ABC' ]

            # map to the data
            values = [ map( f, states ) for f in funcs ]
            
            # filter for true value
            trues  = [ filter ( istrue, v) for v in values ]

            # true values 
            A, B, C = trues
            
            # this will only be the same if ranks are properly used!
            EQ( len(states), 6)
            EQ( len(A), 6)
            EQ( len(B), 6)
            EQ( len(C), 3)
        
    def test_rules( self ):
        """Testing rules (stress test)
        
        Generates lots of random rules and then compares the results 
        when executed in python and with the engine
        """
        EQ = self.assertEqual

        # valid nodes
        nodes  = string.uppercase[:]

        #
        # Initializes a bunch of nodes to random values
        #
        values = [ choice( [True, False] ) for node in nodes ]
        init = [ '%s=%s' % (n,v) for n,v in zip(nodes, values) ]
        
        init_text = join(init) + '\n'

        operators = 'and or '.split()
        body  = []
  
        #    
        # for each node it attempts to build a complicated random expression like:
        #
        # (N or (J and B and M or not Z)) and not G
        #  
        # places nodes, operators and parentheses randomly (but syntactically correct)
        # then executes the rules in python but also with the engine in synchronous 
        # mode and compares the outputs
        # 
        for node in nodes:
            
            # how many nodes per rule
            targets = [ choice( nodes ) for step in range( randint(2, 8) ) ]
            size = len( targets ) - 1

            # insert some parentheses
            if randint(1, 100) > 30:
                for i in range(2):
                    half = size/2
                    left, right = randint(0, half), randint(half, size)
                    targets[left]  = '(' + targets[left]
                    targets[right] = targets[right] + ')'

            # add 'not' operators every once in a while
            if randint(1, 100) > 30:
                for steps in range( 2 ):
                    index = randint(0, size )
                    targets[index] = 'not ' + targets[index]
            
            # insert 'and/or' operators in between the nodes
            opers   = [ choice( operators ) for t in targets ][:-1]
            for index, oper in enumerate ( opers ):
                targets.insert( 2*index+1, oper)

            line = join( targets, sep= ' ')
            body.append( line )

        #
        # now that we have the expressions
        # generate python and engine representations
        #
        py_text, bool_text = [], []
        newts = [ 'n%s' % node for node in nodes ]
        for line, newt, node in zip(body, newts, nodes):
            py_text.append( '%s = %s' % (newt, line) )    
            bool_text.append( '1: %s* = %s' % (node, line) )    

        # needs this to emulate synchronous updating
        py_text.append( join(nodes, sep=', ') + ' = ' + join( newts, sep=', ') )

        py_text   = join( py_text )
        bool_text = join( bool_text )
        full_text = init_text + py_text
        
        # execute the code in python for a number of steps
        # having too many steps is bad as it falls into a steady state
        steps = 4
        exec (init_text)
        for i in range( steps ):
            exec (py_text in locals())
        
        # see the full text here
        #print full_text
        
        text = init_text + bool_text 

        # print text
        # execute the code with the engine
        states = get_states(mode='sync', text=text, steps=steps)
        last   = states[-1]
        
        # checks all states for equality with both methods
        for attr in nodes:
            oldval = locals()[attr]
            newval = getattr(last, attr )
            #print attr, oldval, newval
            EQ( oldval, newval )

def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase( EngineTest )
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner( verbosity=2 ).run( get_suite() )  
    

