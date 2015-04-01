"""
Analysis of the PSID for PS 1 in Gianluca Violante's quantitative
macro course

@author : Spencer Lyon <spencer.lyon@stern.nyu.edu>
@date : 2015-02-04 16:57:38

"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as sm

pd.set_option("use_inf_as_null", True, "display.width", 180)

cols70 = {"1970_INT_": "INT_1970",        # (V1102)
          "LABOR_INC_HEAD": "Income_70",  # (V1196)
          }

cols95 = {"1995_INTERVIEW_": "INT_1995",            # (ER5002)
          "LABOR_INCOME_OF_HEAD1994": "Income_95",  # (ER6980)
          }

colsIND = {"1968_ID_OF_FATHER": "FN_Father",           # (ER32016)
           "PERSON_NUMBER68": "PN",                    # (ER30002)
           "1968_INTERVIEW_NUMBER": "FN",              # (ER30001)
           "1970_INTERVIEW_NUMBER": "INT_1970",        # (ER30043)
           "1995_INTERVIEW_NUMBER": "INT_1995",        # (ER33201)
           "SEX_OF_INDIVIDUAL": "Gender",              # (ER32000)
           "AGE_OF_INDIVIDUAL70": "Age_70",            # (ER30046)
           }

colsPID = {"# 1968_INTERVIEW_NUMBER_OF_INDIVIDUAL": "FN",          # (PID1)
           "PERSON_NUMBER_OF_INDIVIDUAL": "PN",                    # (PID2)
           "1968_INTERVIEW_NUMBER_OF_BIRTH_FATHER": "FN_Father",   # (PID18)
           "PERSON_NUMBER_OF_BIRTH_FATHER": "PN_Father",           # (PID19)
           }

# ---------------- #
# Import Functions #
# ---------------- #


def get_store(fn="/Users/sglyon/DataSets/PSID/PSID.hdf", mode="r"):
    return pd.HDFStore(fn, mode=mode)


def get_psid_file(store, fn, cols, rename_dict):
    df = store.select(fn, columns=cols)
    df.rename(columns=rename_dict, inplace=True)
    return df


def get_pid(cols=colsPID.keys(), rename_dict=colsPID, store=get_store()):
    out = get_psid_file(store, "PID2011ER", cols, rename_dict)
    store.close()
    return out


def get_ind(cols=colsIND.keys(), rename_dict=colsIND, store=get_store()):
    out = get_psid_file(store, "IND2011ER", cols, rename_dict)
    store.close()
    return out


def get_f70(cols=cols70.keys(), rename_dict=cols70, store=get_store()):
    out = get_psid_file(store, "FAM1970", cols, rename_dict)
    store.close()
    return out


def get_f95(cols=cols95.keys(), rename_dict=cols95, store=get_store()):
    out = get_psid_file(store, "FAM1995", cols, rename_dict)
    store.close()
    return out


def set_FN_PN_index(df, sort=True, inplace=True):
    if inplace:
        df.set_index(["FN", "PN"], inplace=True)
        df2 = df
    else:
        df2 = df.set_index(["FN", "PN"])

    if sort:
        # this is our copy or inplace was true, so sorting in place is ok here
        df2.sort_index(inplace=True)

    return df2

# ------------- #
# Organize data #
# ------------- #


def clean_data(d70, d95, ind, pid):
    # Bring (PN, FN, gender, age in 1970) into d70
    d70 = pd.merge(d70, ind[["FN", "PN", "INT_1970", "Gender", "Age_70"]],
                   on="INT_1970")

    # Keep only those males who meet the age criterion
    male70 = d70.query("35 <= Age_70 <= 45 & Gender == 1")

    # Now, bring (FN, PN, Gender) into the 95 dataset
    d95 = pd.merge(d95,
                   ind[["FN", "PN", "INT_1995", "Gender"]],
                   on="INT_1995")

    # keep just males (potential sons) part of the SRC survey (FN < 3000)
    son95 = d95.query("Gender == 1 & FN < 3000")

    # Bring FN_Father and PN_Father into son95
    son95_f = pd.merge(son95, pid, on=["FN", "PN"])

    # Finally, bring sons and fathers together, only keeping useful columns
    df = pd.merge(male70[["Income_70", "FN", "PN"]],
                  son95_f[["Income_95", "FN", "PN", "FN_Father", "PN_Father"]],
                  left_on=["FN", "PN"],
                  right_on=["FN_Father", "PN_Father"],
                  suffixes=("__Father", "__Son"))

    return df


# -------- #
# Analysis #
# -------- #

def do_analysis(df):
    df["rank_70"] = df["Income_70"].rank()
    df["rank_95"] = df["Income_95"].rank()
    df["logy_70"] = np.log(df["Income_70"])
    df["logy_95"] = np.log(df["Income_95"])

    lm_income = "np.log(Income_95) ~ np.log(Income_70)"
    lm_rank = "rank_95 ~ rank_70"

    reg_income_drop = sm.ols(lm_income, df, missing="drop").fit()
    reg_income_1 = sm.ols(lm_income, df.replace(0.0, 1.0)).fit()
    reg_income_100 = sm.ols(lm_income, df.replace(0.0, 100.0)).fit()
    reg_rank = sm.ols(lm_rank, df, missing="drop").fit()

    return (reg_income_drop, reg_income_1, reg_income_100, reg_rank)


def main():
    # Load in data
    d70 = get_f70()
    d95 = get_f95()
    ind = get_ind()
    pid = get_pid()

    df = clean_data(d70, d95, ind, pid)

    return do_analysis(df)


# ---------------------------
#  The code below is a more brute force way of showing that the merge is right
# son95["ID"] = zip(son95.FN, son95.PN)
# dad70["ID_Child"] = zip(dad70.FN_Child, dad70.PN_Child)
# THEsons = son95[son95.ID.isin(dad70.ID_Child)]
# df["ID_Child"] = zip(df.FN_Child, df.PN_Child)
# all(THEsons.ID.isin(df.ID_Child))  # should be true
# ---------------------------
