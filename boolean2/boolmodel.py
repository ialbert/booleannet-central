
from . import util, state, tokenizer

from .ruleparser import Parser

class BoolModel(Parser):
    """
    Maintains the functionality for all models
    """

    def initialize(self, missing=None, defaults={} ):
        """
        Initializes the model, needs to be called to reset the simulation 
        """

        # create a new lexer                
        self.lexer = tokenizer.Lexer().lexer
        
        self.parser.old = state.State()
        self.parser.new = state.State()
       
        # references must be attached to the parser class 
        # to be visible during parsing
        self.states = self.parser.states = [ self.parser.old ]

        # parser the initial data
        list(map( self.local_parse, self.init_lines ))

        # deal with uninitialized nodes
        if self.uninit_nodes:
            if missing:
                for node in self.uninit_nodes:
                    value = missing( node )

                    self.parser.RULE_SETVALUE( self.parser.old, node, value, None)
                    self.parser.RULE_SETVALUE( self.parser.new, node, value, None)
            else:
                util.error( 'uninitialized nodes: %s' % list(self.uninit_nodes))

        # override any initalization with defaults
        for node, value in list(defaults.items()):
            self.parser.RULE_SETVALUE( self.parser.old, node, value, None)
            self.parser.RULE_SETVALUE( self.parser.new, node, value, None)
        

        # will be populated upon the first call
        self.lazy_data = {}

    @property
    def first(self):
        "Returns the first state"
        return self.states[0]

    @property
    def last(self):
        "Returns the last state"
        return self.states[-1]

    @property
    def data(self):
        """
        Allows access to states via a dictionary keyed by the nodes
        """
        # this is an expensive operation so it loads lazily
        assert self.states, 'States are empty'
        if not self.lazy_data:
            nodes = list(self.first.keys())
            for state in self.states:
                for node in nodes:
                    self.lazy_data.setdefault( node, []).append( state[node] )
        return self.lazy_data

    def state_update(self):       
        """Internal update function"""
        p = self.parser       
        p.old = p.new
        p.new = p.new.copy()                     
        p.states.append( p.new )

    def local_parse( self, line ):
        "Used like such only to keep track of the last parsed line"
        global LAST_LINE
        LAST_LINE = line
        return self.parser.parse( line )

    def iterate( self, steps, shuffler=util.default_shuffler, **kwds ):
        """
        Iterates over the lines 'steps' times. Allows other parameters for compatibility with the plde mode
        """
        
        # needs to be reset in case the data changes
        self.lazy_data = {}

        for index in range(steps):
            self.parser.RULE_START_ITERATION( index, self )
            self.state_update()
            for rank in self.ranks:
                lines = self.update_lines[rank]
                lines = shuffler( lines )
                list(map( self.local_parse, lines )) 

    def save_states(self, fname):
        """
        Saves the states into a file
        """
        if self.states:
            fp = open(fname, 'wt')
            cols = [ 'STATE' ] + list(self.first.keys()) 
            hdrs = util.join ( cols )
            fp.write( hdrs )
            for state in self.states:
                cols = [ state.fp() ] + list(state.values())
                line = util.join( cols )
                fp.write( line )
            fp.close()
        else:
            util.error( 'no states have been created yet' )

    def detect_cycles( self ):
        "Detect the cycles in the current states of the model"
        return util.detect_cycles( data=self.fp() )                

    def report_cycles(self ):
        """
        Convenience function that reports on steady states
        """
        index, size = self.detect_cycles()
        
        if size == 0:
            print(("No cycle or steady state could be detected from the %d states" % len(self.states)))
        elif size==1:
            print(("Steady state starting at index %s -> %s" % (index, self.states[index] )))
        else:
            print(("Cycle of length %s starting at index %s" % (size, index)))
    
    def fp(self):
        "The models current fingerprint"
        return [ s.fp() for s in self.states ]

                 
if __name__ == '__main__':
    

    text = """
    A  =  B =  C = False
    D  = True
    
    5: A* = C and (not B)
    10: B* = A
    15: C* = D
    20: D* = B 
    """

    model = BoolModel( mode='async', text=text )

    model.initialize(  )
        
    print(('>>>', model.first))

    model.iterate( steps=2 )
    
    print((model.fp()))
    model.report_cycles()
    model.save_states( fname='states.txt' )

    # detect cycles from a list of states
    states = ['S1', 'S2', 'S1', 'S2', 'S1', 'S2']
    print() 
    print(('States %s -> Detect cycles %s' % (states, util.detect_cycles( states ) )))


       
