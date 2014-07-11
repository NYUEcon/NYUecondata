"""
Runs peaktrough.py, which generates Cooley-Rupert figures for specified
series from FRED.

Execute peaktrough.py first, then run this program. 

Written by Dave Backus under the watchful eye of Chase Coleman and Spencer Lyon 
Date:  July 10, 2014 
"""
from peaktrough import *

# one at a time 
# manhandle_freddata("GDPC1", saveshow="save")

# all at once with map -- needs lhs variables to run
# question:  can we change the saveshow par inside map?
fred_series = ["GDPC1", "PCECC96", "GPDIC96", "OPHNFB"]
gdpc1, pcecc96, gpdic96, ophnfb = map(manhandle_freddata, fred_series)



