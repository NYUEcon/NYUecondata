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

# all at once with map -- needs lhs variables to run
# question:  can we change the saveshow par inside map?
fred_series = ["GDPC1", "PCECC96", "GPDIC96", "OPHNFB"]
gdpc1, pcecc96, gpdic96, ophnfb = map(manhandle_freddata, fred_series)



