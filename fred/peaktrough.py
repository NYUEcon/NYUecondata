"""
Authors: Chase Coleman and Spencer Lyon
Date: 06/24/2014
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.io.data import DataReader


def chopseries(data, indices, periods=40):
    """
    Takes a series and turns it into a data frame starting at each index
    and running for the number of periods specified (default is 40)
    """
    # Number or series to plot
    n = len(indices)

    new_data = pd.DataFrame(np.empty((periods, n)))

    for num, date in enumerate(indices):
        date_loc = data.index.get_loc(date)
        try:
            new_data[num] = data.ix[date_loc:date_loc+periods].values
        except:
            the_values = data.ix[date_loc:].values
            length = the_values.size
            stupiddata = np.concatenate([the_values.squeeze(),
                                        np.nan*np.ones(periods-length)])
            new_data[num] = stupiddata

    return new_data


def manhandle_freddata(fred_series, nperiods=40,
                       changetype="Percent", start="01/01/1972"):
    """
    This function takes a string that corresponds to a data series from
    FRED and creates a dataframe that takes this series and creates a
    new series that shows the change of the series starting at the
    beginning of every business cycle and ending nperiods quarters later
    using either log differences or percent change.

    By default it will start at the beginning of 1972 and additionally
    data should be quarterly

    If you would like to use multiple series, use python's map function:
    map(manhandle_freddata, [list of fred_series])
    """

    fred_data = DataReader(fred_series, "fred", start)

    # Get quarterly recession dates from FRED
    rec_dates = DataReader("USRECQ", "fred", start)
    one_vals = np.where(rec_dates == 1)[0]
    rec_start = [one_vals[0]]

    # Find the beginning of the recession dates (Don't include ones that
    # begin within three years of a previous one)
    for d in one_vals:
        if d > max(rec_start) + 12:
            rec_start.append(d)

    rec_startind = rec_dates.index[rec_start]

    chopped_data = chopseries(fred_data, rec_startind, periods=nperiods)

    if changetype=="Percent":
        chopped_change = ((chopped / chopped.iloc[0] - 1)*100)
    elif changetype=="Log":
        chopped_change = np.log(chopped).diff()

    fig = plt.figure()
    chopped_change.plot()
    plt.show()

    return chopped_change


manhandle_freddata("GDPC1")

# chopped = chopseries(data["GDPC1"], rec_startind)



# Get Real GDP, Real Personal Consumption, Nonresidential Investment,
# and Output per Hour from FRED
# fred_names = ["GDPC1", "PCECC96", "GPDIC96", "OPHNFB"]
# data = DataReader(fred_names, "fred", "01/01/1972")
