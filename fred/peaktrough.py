"""
Authors: Chase Coleman and Spencer Lyon
Date: 06/24/2014
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.io.data import DataReader


# Get Real GDP, Real Personal Consumption, Nonresidential Investment,
# and Output per Hour from FRED
fred_names = ["GDPC1", "PCECC96", "GPDIC96", "OPHNFB"]
data = DataReader(fred_names, "fred", "01/01/1972")

# Get quarterly recession dates from FRED
rec_dates = DataReader("USRECQ", "fred", "01/01/1972")
one_vals = np.where(rec_dates == 1)[0]
rec_start = [one_vals[0]]

# Find the beginning of the recession dates (Don't include ones that
# begin within three years of a previous one)
for d in one_vals:
    if d > max(rec_start) + 12:
        rec_start.append(d)

rec_startind = rec_dates.index[rec_start]

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
            stupiddata = np.concatenate([the_values, np.nan*np.ones(40-length)])
            new_data[num] = stupiddata

    return new_data

chopped = chopseries(data["GDPC1"], rec_startind)
