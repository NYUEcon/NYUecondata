"""
Runs peaktrough.py, which generates Cooley-Rupert figures for specified
series from FRED.

Execute peaktrough.py first, then run this program.

Written by Dave Backus under the watchful eye of Chase Coleman and Spencer Lyon
Date:  July 10, 2014
"""
# import functions from peaktrough.py. * means all of them
# generates the msg "UMD has deleted: peaktrough" which means it reloads
from peaktrough import *


def kwarg_map(func, my_args, **kwargs):
    """
    Apply the `map` to `func` over all elements in `my_args`, where
    each time `func` is called, any additional keywords passed to this
    function are passed along to `func`.

    Parameters
    ----------
    func : function
        The function to be mapped

    my_args : iterable
        An iterable that serves as the input value to func within map

    kwargs : optional
        Any other keyword arguments that should be passed along to func
        when it is called for each element in my_args

    Returns
    -------
    out : list
        The list of return values after mapping my_args on func

    Examples
    --------
    >>> fred_series = ["GDPC1", "PCECC96", "GPDIC96", "OPHNFB"]
    >>> out = kwarg_map(manhandle_freddata, fred_series,
    ... saveshow="show")  # shows plots, doesn't save them.

    """
    return map(lambda x: func(x, **kwargs), my_args)

# do plots one at a time
manhandle_freddata("GDPC1", saveshow="show")
print("aaaa")

# do plots all at once with map
fred_series = ["GDPC1", "PCECC96", "GPDIC96", "OPHNFB"]

# uses default saveshow parameter
gdpc1, pcecc96, gpdic96, ophnfb = map(manhandle_freddata, fred_series)

print("xxxx")
# lets us change saveshow parameter
gdpc1, pcecc96, gpdic96, ophnfb = map(lambda s:
    manhandle_freddata(s, saveshow="save"), fred_series)

print("yyyy")
# skip lhs (this doesn't seem to work, not sure why)
map(lambda s:
    manhandle_freddata(s, saveshow="show"), fred_series)

print("zzzz")


