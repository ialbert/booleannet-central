import unittest
import testbase

# these are the module names that will be tested
modules = "test_sync"

def get_suite():
    suite = unittest.TestSuite()

    # split into individual names
    names = modules.split()
    
    # import and run the suite in each
    for name in names:
        mod = __import__( name)
        suite.addTest( mod.get_suite() )
    
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner( verbosity=2 ).run( get_suite() ) 
