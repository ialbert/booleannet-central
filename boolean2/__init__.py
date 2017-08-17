"""
Boolean Network Library

"""
import sys, re, os

__VERSION__ = '1.2.0-beta'

from . import util

# require python 2.4 or higher
if sys.version_info[:2] < (2, 5):
    util.error("this program requires python 2.5 or higher" )

from . import ruleparser, boolmodel, timemodel, tokenizer

from .tokenizer import modify_states

def Model( text, mode):
    "Factory function that returns the proper class based on the mode"

    # the text parameter may be a file that contains the rules
    if os.path.isfile( text ):
        text = file(text, 'rt').read()

    # check the validity of modes
    if mode not in ruleparser.VALID_MODES:
        util.error( 'mode parameter must be one of %s' % VALID_MODES)

    # setup mode of operation
    if mode == ruleparser.TIME:
        return timemodel.TimeModel(mode='time', text=text)
    elif mode == ruleparser.PLDE:
        # matplotlib may not be installed 
        # so defer import to allow other modes to be used
        from .plde import model
        return model.PldeModel( mode='plde', text=text)
    else:
        return boolmodel.BoolModel( mode=mode, text=text )

def all_nodes ( text ):
    "Returns all the nodes in the text"
    tokens = tokenizer.tokenize( text )
    return tokenizer.get_nodes ( tokens )

def test():
    text = """
    A  =  B =  C = False
    D  = True
    
    5: A* = C and (not B)
    10: B* = A
    15: C* = D
    20: D* = B 
    """

    model = Model( mode='plde', text=text )
    model.initialize(  )
    model.iterate( steps=10, fullt=2)
    
    print((all_nodes ( text )))
    #for i in range(12):
    #    print (model.next()

if __name__ == '__main__':
    test()
