import re

from booleannet import util, tokenizer
from booleannet import state as state_mod
from booleannet.ruleparser import Parser

# Node names match the lexer. A value of None means "pick true or false once".
_ASSIGN = re.compile(r"^([A-Za-z_+\-][A-Za-z0-9_+\-]*)=(1|0|\?|true|false|random)$", re.I)
_VALUES = {"1": True, "0": False, "?": None, "true": True, "false": False, "random": None}


def parse_state(text):
    """Parse ``A=1 B=0 C=?`` into ``{node: True|False|None}``.

    Spaces and newlines separate assignments. ``#`` starts a comment.
    A later assignment for the same node wins. ``None`` means random.
    """
    spec = {}
    for raw in text.splitlines():
        line = raw.split("#", 1)[0]
        for tok in line.split():
            match = _ASSIGN.match(tok)
            if not match:
                util.error("invalid initial condition: %s" % tok)
            spec[match.group(1)] = _VALUES[match.group(2).lower()]
    return spec


class BoolModel(Parser):
    """
    Maintains the functionality for all models
    """

    def initialize(self, missing=None, defaults=None, state=None):
        """
        Initializes the model, needs to be called to reset the simulation.

        ``state`` is initial-condition text or a dict of node to
        ``True``, ``False``, or ``None`` (random). It replaces the
        init lines in the rules. Nodes not listed are filled by
        ``missing``, which defaults to a random boolean.
        ``defaults`` still overrides ``state``.
        """
        if defaults is None:
            defaults = {}
        else:
            defaults = dict(defaults)

        # create a new lexer                
        self.lexer = tokenizer.Lexer().lexer
        
        self.parser.old = state_mod.State()
        self.parser.new = state_mod.State()
       
        # references must be attached to the parser class 
        # to be visible during parsing
        self.states = self.parser.states = [ self.parser.old ]

        if state is None:
            init_lines = self.init_lines
            pending = self.uninit_nodes
        else:
            spec = state if isinstance(state, dict) else parse_state(state)
            chosen = {}
            for node, value in spec.items():
                if node not in self.nodes:
                    util.error("unknown node: %s" % node)
                if value is None:
                    value = util.randbool(node)
                chosen[node] = value
            chosen.update(defaults)
            defaults = chosen
            init_lines = []
            pending = self.update_nodes - set(defaults)
            if missing is None:
                missing = util.randbool

        # parser the initial data
        list(map( self.local_parse, init_lines ))

        # deal with uninitialized nodes
        if pending:
            if missing:
                for node in pending:
                    value = missing( node )

                    self.parser.RULE_SETVALUE( self.parser.old, node, value, None)
                    self.parser.RULE_SETVALUE( self.parser.new, node, value, None)
            else:
                util.error( 'uninitialized nodes: %s' % list(pending))

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
            print("No cycle or steady state could be detected from the %d states" % len(self.states))
        elif size==1:
            print("Steady state starting at index %s -> %s" % (index, self.states[index] ))
        else:
            print("Cycle of length %s starting at index %s" % (size, index))
    
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
        
    print('>>>', model.first)

    model.iterate( steps=2 )
    
    print(model.fp())
    model.report_cycles()
    model.save_states( fname='states.txt' )

    # detect cycles from a list of states
    states = ['S1', 'S2', 'S1', 'S2', 'S1', 'S2']
    print() 
    print('States %s -> Detect cycles %s' % (states, util.detect_cycles( states ) ))


       