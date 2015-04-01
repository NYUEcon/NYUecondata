"""
Working with PSID in python

@author : Spencer Lyon <spencer.lyon@stern.nyu.edu>
@date : 2015-02-04 09:02:56

use the read_csv option `usecols` to only keep what we need

"""
import re
import os
import gc
import os.path
import zipfile
import requests
import lxml.html
import numpy as np
import pandas as pd


#  ----------- #
#  Downloading #
#  ----------- #

# Define lookup that maps years into request numbers.
file_year = map(str, list(range(1968, 1998)) + list(range(1999, 2012, 2)))
request_numbers = map(str, ([1056] + list(range(1058, 1083)) +
                            list(range(1047, 1052)) +
                            [1040, 1052, 1132, 1139, 1152, 1156]))
file_lookup = dict(zip(file_year, request_numbers))
file_lookup["ind"] = "1053"


def start_psid_session(user=None, password=None):
    """
    Use user supplied login details to log in to umich site for PSID
    download
    """
    login_url = "http://simba.isr.umich.edu/u/Login.aspx"

    # start html session so we can log in
    session = requests.session()
    start = session.get(login_url)
    html = start.text
    root = lxml.html.fromstring(html)

    # Stuff so we can log in
    EVAL = root.xpath('//input[@name="__EVENTVALIDATION"]')[0].attrib['value']
    VIEWSTATE = root.xpath('//input[@name="__VIEWSTATE"]')[0].attrib['value']

    acc_pwd = {'ctl00$ContentPlaceHolder1$Login1$UserName': user,
               'ctl00$ContentPlaceHolder1$Login1$Password': password,
               'ctl00$ContentPlaceHolder1$Login1$LoginButton': 'Log In',
               '__EVENTTARGET': '',
               '__EVENTARGUMENT': '',
               '__VIEWSTATE': VIEWSTATE,
               '__EVENTVALIDATION': EVAL}

    # Send login message to PSID site
    session.post(login_url, data=acc_pwd)

    # Check for login
    z = session.get('http://simba.isr.umich.edu/data/data.aspx')
    tf2 = 'Logout' in str(z.content)
    print('Successful login: %s' % (tf2))

    return session


# Function to download PSID zip file
def download_psid(number, local_filename, session):
    """
    Download a zip file form the PSID and save to local_filename
    """
    request_start = 'http://simba.isr.umich.edu/Zips/GetFile.aspx?file='

    # Get the file using requests
    r = session.get(request_start + number, stream=True)

    with open(local_filename, 'wb') as f:

        # Write it out in chunks incase it's big
        for chunk in r.iter_content(chunk_size=1024):

            if chunk:
                f.write(chunk)
                f.flush()

    return local_filename


# Extracting PSID using psid_unzip.
def psid_unzip(filename, extractall=False):

    zfile = zipfile.ZipFile(filename)

    def keep_file(n):
        if extractall:
            return True
        else:
            return ".sas" in name or ".txt" in name or ".pdf" in name

    for name in zfile.namelist():

        # Only take out the files we want
        if keep_file(name):

            (dirname, filename) = os.path.split(name)

            if ".pdf" in name:  # Different directory for Codebooks
                dirname = dirname + "Codebooks"
            if ".txt" in name:
                nascii = name  # Keep track of ascii name
            if ".sas" in name:
                nsas = name  # Keep track of sas name

            print("Decompressing %s on %s" % (filename, dirname))

            if dirname != '':
                if not os.path.exists(dirname):
                    os.makedirs(dirname)

            zfile.extract(name, dirname)  # Extract file

    return (nsas, nascii)


def sascii2csv(sas_name, ascii_name, csv_name, remove_orig=True):
    """
    Read in ascii data from SAS commands and write out csv
    """
    # Open sas file
    x = open(sas_name, "r")
    dat = x.read()
    dat_split = dat.split('\n')

    # RE for variable designation
    re_var = "^\s*(?P<variable>\S+)\s+"

    # RE for variable label
    re_label = '[(LABEL)(label)]\s*=\s*"(?P<label>[^"]+)"'

    # RE for variable format
    re_format = "[(FORMAT)(format)]\s*=\s*(?P<format>\S+)\s"

    # RE for variable position
    re_length = "\s*(?P<length1>\d*)\s*-\s*(?P<length2>\d*)\s*"

    meta = []

    for dstr in dat_split:
        res_var = re.search(re_var, dstr)  # Find variable name in line
        res_label = re.search(re_label, dstr)  # Find variable label
        res_format = re.search(re_format, dstr)  # Find variable format

        if not (res_var is None or res_label is None or res_format is None):

            # Now that we have a verified variable name...

            # Find position RE
            counts = re.search(res_var.group("variable")+re_length, dat)
            l1 = int(counts.group("length1"))  # Grab out first position
            l2 = int(counts.group("length2"))  # Grab out second position

            # Add to meta data
            meta += [{"variable": res_var.group("variable"),
                      "label": res_label.group("label"),
                      "format": res_format.group("format"),
                      "l1": l1,
                      "l2": l2,
                      "l3": l2 - l1 + 1}]

    # Get relevant descriptions
    names = [z["label"] for z in meta]
    lengths = [z["l3"] for z in meta]
    del meta

    # Use numpy to read fixed width file and write as .csv
    data = np.genfromtxt(ascii_name, names=names, delimiter=lengths)
    np.savetxt(csv_name, data, delimiter=',',
               header=','.join(data.dtype.names))
    del data

    if remove_orig:
        os.remove(sas_name)
        os.remove(ascii_name)


def download_unzip_csv_psid(f_name, request_num, session, to_csv=True,
                            remove_orig=True, verbose=True):
    """
    Download a family data set
    """
    # Download zip file
    if verbose:
        print("Downloading %s" % f_name)

    x = download_psid(str(request_num), f_name, session)

    # Unzip
    if verbose:
        print("Unzipping %s" % f_name)

    sas_name, ascii_name = psid_unzip(f_name)

    if to_csv:
        if verbose:
            print("Converting %s to csv" % ascii_name)

        # generate csv_name and convert to csv
        csv_name = f_name.strip(".zip") + ".csv"
        sascii2csv(sas_name, ascii_name, csv_name, remove_orig=remove_orig)

    if remove_orig:
        os.remove(f_name)

    gc.collect()


def download_all_family_data(session, to_csv=True, **kwargs):
    """
    Download all family data sets
    """
    for (fy, rn) in file_lookup.copy().pop("ind").items():
        fn = "FAM" + fy + ".zip"
        download_unzip_csv_psid(fn, rn, session, to_csv=to_csv, **kwargs)

    return


def download_ind_cross_year(session, to_csv=True, **kwargs):
    """
    Download the cross year individual file
    """
    download_unzip_csv_psid("IND2011ER.zip", str(1053), session,
                            to_csv=to_csv, **kwargs)

    return


def download_parentfile(session, to_csv=True, **kwargs):
    """
    Download the cross year individual file
    """
    download_unzip_csv_psid("PID2011ER.zip", str(1123), session,
                            to_csv=to_csv, **kwargs)

    return


def download_all_data(session, to_csv=True, **kwargs):
    """
    Call the download ind and download all family functions
    """
    download_ind_cross_year(session, to_csv=True, **kwargs)
    download_all_family_data(session, to_csv=True, **kwargs)
    return


#  -------- #
#  Cleaning #
#  -------- #


def clean_indfile_names(df):
    """
    Most of the columns in the PSID individual file have many
    underscores in between the variable name and the year. The next few
    lines remove those cases and re- assigns the column names.

    This is necessary for us to save that data to hdf in table format

    """
    cols = pd.Series(df.columns, dtype=str)
    c2 = cols.str.extract("(.+?)__+(\d\d)")
    cols2 = c2[0] + c2[1]
    cols2 = cols2.fillna(cols)
    df.cols = cols2

    return df


def csv2hdf(csv_fn, hdf_fn, hdf_gn=None, hdf_mode="a",
            extra_func=None):
    """
    Move the file csv_fn to an HDF file.

    Parameters
    ----------
    csv_fn : string
        The file name for the csv

    hdf_fn: string
        The name of the hdf file to write to

    hdf_gn: string, optional
        A string specifying the `path` to the group to contain the
        dataset. If none is given, the data set is saved to `/fn`, where
        fn is the root of csv_fn

    hdf_mode: string, optional(default="a")
        The open mode for the hdf file. Default is append

    extra_func: function, optional(default=None)
        An extra function the user can supply to clean or otherwise
        alter the data set after reading in from csv, but before saving
        to hdf

    Returns
    -------
    None

    Notes
    -----
    This function tries to write the data set in table form, but if it
    cannot it will fallback to writing in fixed form.

    For a discussion on the differences see the pandas manual

    """
    df = pd.read_csv(csv_fn)

    if extra_func is not None:
        df = extra_func(df)

    if hdf_gn is None:
        # split to path/file then chop last 4 characters off (`.csv`)
        hdf_gn = os.path.split(csv_fn)[1][:-4]

    try:
        df.to_hdf(hdf_fn, hdf_gn, mode=hdf_mode, format="table",
                  complib="blosc")
        print("Added %s to %s" % (hdf_gn, hdf_fn))
    except:
        print("WARN: Couldn't store %s as table. Using fixed" % hdf_gn)
        df.to_hdf(hdf_fn, hdf_gn, mode=hdf_mode, format="fixed",
                  complib="blosc")

    return


def _convert_to_4_digit_year(yr):
    print("recieved yr: %s" % yr)
    if len(yr) == 4:
        return yr

    if len(yr) == 1:
        return "200" + yr

    if len(yr) == 3:
        raise ValueError("Can't parse three digit year")

    iy = int(yr)

    if 0 <= iy <= 9:  # 200x
        return "20" + yr

    elif 10 < iy <= int(str(datetime.datetime.now().year)[2:]):
        return "20" + yr

    else:  # assuming in 1900's
        return "19" + yr


if __name__ == '__main__':
    import glob
    import argparse
    import datetime
    from textwrap import dedent
    d_help = dedent("""\
    Download the specified data file. If argument begins with a, all files
    will be downloaded. If it begins with i, only the cross-year individual
    file will be downloaded. If it is of the form fYY or fYYYY then only the
    family file for the given year will be downloaded
    """)

    # create parser and add arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--download",
                        help=d_help)
    parser.add_argument("--hdf",
                        help="Convert csv files to hdf named PSID.hdf",
                        action="store_true")
    parser.add_argument("-u", "--username",
                        help="Specify username for PSID website")
    parser.add_argument("-p", "--password",
                        help="Specify password for PSID website")

    args = parser.parse_args()

    # Handle download arg
    if args.download:
        # make sure we have a user_name and password
        if args.username is None or args.password is None:
            msg = dedent("""\
            Must supply username and password. Example syntax:

            `python psid.py -u USERNAME -p PASSWORD -d f75 --hdf`

            If you don't yet have an account, go to http://simba.isr.umich.edu
            and create one
            """)
            raise ValueError(msg)

        a = args.download
        session = start_psid_session(user=args.username,
                                     password=args.password)
        if a.startswith("a"):  # download all
            download_all_data(session)

        elif a.startswith("i"):  # download individual file
            download_ind_cross_year(session, to_csv=True)

        elif a.startswith("p"):  # download parent id file
            download_parentfile(session, to_csv=True)

        else:
            # download single family file
            m = re.match("f?(\d+)", a.lower())
            if m is not None:
                yr = m.groups()[0]
                yr = _convert_to_4_digit_year(yr)
                rn = file_lookup[yr]
                fn = "FAM" + yr + ".zip"
                download_unzip_csv_psid(fn, rn, session, to_csv=True)
            else:
                raise ValueError("Could not parse download option")

    # Handle hdf arg
    if args.hdf:
        fnames = glob.glob("./*.csv")  # get csv file names.
        fnames.sort(reverse=True)  # Sorting to put IND file at top
        for f in fnames:
            if f.lower().startswith("ind"):
                csv2hdf(f, "PSID.hdf", extra_func=clean_indfile_names)
            else:
                csv2hdf(f, "PSID.hdf")
