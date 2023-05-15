import pandas as pd
from datetime import date, datetime, timedelta
import os
import csv

# from scipy import stats
import scipy.stats as stats

# define dictionary
comp_dict = {
    "FanGraphs Leaderboard.csv": "fgl_pitchers_10_ip.csv",
    "FanGraphs Leaderboard (1).csv": "fgl_pitchers_30_ip.csv",
    "FanGraphs Leaderboard (2).csv": "fgl_hitters_40_pa.csv",
    "FanGraphs Leaderboard (3).csv": "fgl_hitters_last_14.csv",
    "FanGraphs Leaderboard (4).csv": "fgl_hitters_last_7.csv",
    "FanGraphs Leaderboard (5).csv": "fgl_pitchers_last_14.csv",
    "FanGraphs Leaderboard (6).csv": "fgl_pitchers_last_30.csv",
    "FanGraphs Leaderboard (7).csv": "hitter.csv",
    "FanGraphs Leaderboard (8).csv": "pitcher.csv",
}

for newname, oldname in comp_dict.items():
    os.replace(newname, oldname)

excluded = pd.read_csv("excluded.csv")

dfhitter = pd.read_csv("hitter.csv")
temp_df = dfhitter[["Name", "playerid"]]
dfhitter = dfhitter.drop(columns=["playerid", "mlbamid"])
columns = ["BABIP+", "K%+", "BB%+", "ISO+", "wRC+", "Barrels"]
dfhitter = dfhitter.fillna(0)
dfhitter[columns] = dfhitter[columns].astype("float")

# Get the list of columns to zscore
numbers = dfhitter.select_dtypes(include="number").columns

# Zscore the columns
dfhitter[numbers] = dfhitter[numbers].apply(stats.zscore)

# Add a column for the total z-score
dfhitter["Total Z-Score"] = dfhitter.sum(axis=1).round(2)
dfhitter = dfhitter.merge(temp_df[["Name", "playerid"]], on=["Name"], how="left")

dfhitter.to_csv("hitterz.csv", index=False)

dfpitcher = pd.read_csv("pitcher.csv")
temp_df2 = dfpitcher[["Name", "playerid"]]
dfpitcher = dfpitcher.drop(columns=["playerid", "mlbamid"])
dfpitcher = dfpitcher.fillna(0)

columns2 = ["Stuff+", "Location+", "Pitching+", "Starting", "Relieving"]
dfpitcher[columns2] = dfpitcher[columns2].astype("float")

# Get the list of columns to zscore
numbers2 = dfpitcher.select_dtypes(include="number").columns

# Zscore the columns
dfpitcher[numbers2] = dfpitcher[numbers2].apply(stats.zscore)

# Add a column for the total z-score
dfpitcher["Total Z-Score"] = dfpitcher.sum(axis=1).round(2)
dfpitcher = dfpitcher.merge(temp_df2[["Name", "playerid"]], on=["Name"], how="left")

dfpitcher.to_csv("pitcherz.csv", index=False)
print(dfpitcher)

today = date.today()
today = datetime.strptime(
    "2023-10-31", "%Y-%m-%d"
).date()  # pinning to last day of baseball season


def hitters_preprocessing(filepath):
    df = pd.read_csv(filepath, index_col=["playerid"])

    df["Barrel%"] = df["Barrel%"] = df["Barrel%"].str.rstrip("%").astype("float")
    filter = df[(df["PA"] > 10)]

    df.columns = df.columns.str.replace("[+,-,%,]", "", regex=True)
    df.rename(columns={"K%-": "K", "BB%-": "BB"}, inplace=True)
    df.fillna(0)
    df.reset_index(inplace=True)
    df = df[~df["playerid"].isin(excluded["playerid"])]
    df = df.merge(dfhitter[["playerid", "Total Z-Score"]], on=["playerid"], how="left")

    # df['Barrel'] = df['Barrel'] = df['Barrel'].str.rstrip('%').astype('float')

    filters = df[
        (df["wRC"] > 135)
        & (df["OPS"] > 0.8)
        & (df["K"] < 95)
        & (df["BB"] > 100)
        & (df["Off"] > 1)
        & (df["Barrel"] > 10)
    ].sort_values(by="Off", ascending=False)
    return filters


def sp_preprocessing(filepath):
    df = pd.read_csv(filepath, index_col=["playerid"])

    df.columns = df.columns.str.replace("[+,-,%,]", "", regex=True)
    df.rename(
        columns={"K/BB": "KToBB", "HR/9": "HRPer9", "xFIP-": "XFIPMinus"}, inplace=True
    )
    df.fillna(0)
    df.reset_index(inplace=True)
    df = df[~df["playerid"].isin(excluded["playerid"])]
    df = df.merge(dfpitcher[["playerid", "Total Z-Score"]], on=["playerid"], how="left")

    df["Barrel"] = df["Barrel"] = df["Barrel"].str.rstrip("%").astype("float")
    df["CSW"] = df["CSW"] = df["CSW"].str.rstrip("%").astype("float")

    filters1 = df[
        (df["Barrel"] < 7)
        & (df["Starting"] > 5)
        & (df["GS"] > 1)
        & (df["Pitching"] > 99)
    ].sort_values(by="Starting", ascending=False)
    #   filters2 = df[(df['Barrel'] < 7) & (df['Relieving'] > 1) & (df['Pitching'] > 99)].sort_values(by='Relieving', ascending=False)
    return filters1


#   return filters2


def rp_preprocessing(filepath):
    df = pd.read_csv(filepath, index_col=["playerid"])

    df.columns = df.columns.str.replace("[+,-,%,]", "", regex=True)
    df.rename(
        columns={"K/BB": "KToBB", "HR/9": "HRPer9", "xFIP-": "XFIPMinus"}, inplace=True
    )
    df.fillna(0)
    df.reset_index(inplace=True)
    df = df[~df["playerid"].isin(excluded["playerid"])]
    df = df.merge(dfpitcher[["playerid", "Total Z-Score"]], on=["playerid"], how="left")

    df["Barrel"] = df["Barrel"] = df["Barrel"].str.rstrip("%").astype("float")
    df["CSW"] = df["CSW"] = df["CSW"].str.rstrip("%").astype("float")

    #    filters1 = df[(df['Barrel'] < 7) & (df['Starting'] > 5) & (df['GS'] > 1) & (df['Pitching'] > 99)].sort_values(by='Starting', ascending=False)
    filters2 = df[
        (df["Barrel"] < 7) & (df["Relieving"] > 5) & (df["Pitching"] > 99)
    ].sort_values(by="Relieving", ascending=False)
    #   return filters1
    return filters2


# Preprocess and export the dataframes to Excel workbook sheets
hitdaywindow = [7, 14]
pawindow = [40]
pitchdaywindow = [14, 30]
ipwindow = [10, 30]

df_list = []

with open("weeklyadds.csv", "w+") as f:
    for w in hitdaywindow:
        f.write(f"Hitters Last {w} Days\n\n")
        df = hitters_preprocessing(f"fgl_hitters_last_{w}.csv")
        df_list.append(df)
        df.to_csv(f, index=False)
        f.write("\n")

    for w in pawindow:
        f.write(f"Hitters {w} PA\n\n")
        df = hitters_preprocessing(f"fgl_hitters_{w}_pa.csv")
        df_list.append(df)
        df.to_csv(f, index=False)
        f.write("\n")

    for w in ipwindow:
        f.write(f"SP {w} Innings\n\n")
        df = sp_preprocessing(f"fgl_pitchers_{w}_ip.csv")
        df_list.append(df)
        df.to_csv(f, index=False)
        f.write("\n")
        f.write(f"RP {w} Innings\n\n")
        df = rp_preprocessing(f"fgl_pitchers_{w}_ip.csv")
        df_list.append(df)
        df.to_csv(f, index=False)
        f.write("\n")

    for w in pitchdaywindow:
        f.write(f"Pitchers Last {w} Days\n\n")
        df = sp_preprocessing(f"fgl_pitchers_last_{w}.csv")
        df_list.append(df)
        df.to_csv(f, index=False)
        f.write("\n")
        f.write(f"RP Last {w} Days\n\n")
        df = rp_preprocessing(f"fgl_pitchers_last_{w}.csv")
        df_list.append(df)
        df.to_csv(f, index=False)
        f.write("\n")
