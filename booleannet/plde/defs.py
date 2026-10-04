from math import log, pow
from random import randint, random

def prop( rc, r ):
    'A proportion distribution function with a rate rc and an uncertanity r'
    if randint(0,1):
        return rc + r * random()
    else:
        return rc - r * random()

def hill( conc, h, n ):
    'Hill function with base h and exponent n'
    pval = pow(conc, n)
    return pval / ( pow(h, n) + pval )

