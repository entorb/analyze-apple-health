#!/usr/bin/env python3
# by Dr. Torben Menke https://entorb.net
# https://github.com/entorb/analyze-apple-health
"""
Analyze data.

read out/data-raw-2.tsv
export example data to out/data-type-examples/
convert to pivot table using endDate as index
export month summary for certain data types
"""

from pathlib import Path

import numpy as np
import pandas as pd

Path("out/data-type-examples").mkdir(exist_ok=True)

df = pd.read_csv(
    "out/data-raw-2.tsv",
    sep="\t",
    index_col=0,
    parse_dates=["creationDate", "startDate", "endDate"],
    dtype={
        "type": str,
        "sourceName": "str",
        "sourceVersion": "str",
        "unit": "str",
        "value": "float64",
        "device": "str",
    },
)

print("export out/data-type-examples/")
# print example rows per each type 1st, middle, last
types = sorted(df["type"].unique().tolist())
for t in types:
    df2 = df[df["type"] == t]
    lines = len(df2.index)
    if lines >= 4:  # noqa: PLR2004
        print(" - " + t)
        df2 = df2.iloc[[0, int(lines / 3), int(2 * lines / 3), -1]]
        df2.to_csv(
            f"out/data-type-examples/{t}.tsv",
            sep="\t",
            line_terminator="\n",
        )  # type: ignore


df2 = df.groupby(["sourceName", "type"]).size().reset_index(name="count")
print(df2)
df2.to_csv(
    "out/count_source_type.tsv",
    sep="\t",
    lineterminator="\n",
    index=False,
)

df2 = df.groupby(["type", "sourceName"]).size().reset_index(name="count")
print(df2)
df2.to_csv(
    "out/count_type_source.tsv",
    sep="\t",
    lineterminator="\n",
    index=False,
)

# filter out useless data
# SleepAnalysis: values = 1 -> means it has been done, but no data here
df = df[~((df["type"] == "SleepAnalysis") & (df["value"] == 1))]
# in the pivot I want to drop HeartRate data measured during my cycling activities
df = df[~((df["type"] == "HeartRate") & (df["sourceName"] == "ELEMNT"))]


# pivot
df_pivot = df.pivot_table(index="endDate", columns="type", values="value")

df_pivot.to_csv(
    "out/pivot.tsv",
    sep="\t",
    lineterminator="\n",
)

# calc month average/mean values (without any filtering applied...)
# uncomment data types you do not have in your health data set
df_month = df_pivot.resample("M").agg(
    {
        "BodyMass": np.mean,
        "StepCount": sum,
        "FlightsClimbed": sum,
        "DistanceWalkingRunning": sum,
        "DistanceCycling": sum,
        # "ActiveEnergyBurned": sum,
        # "RestingHeartRate": np.mean,
        "HeadphoneAudioExposure": np.mean,
        # "HeartRate": np.mean, # needs filtering on activity and not
        # "RespiratoryRate": np.mean,
    },  # type: ignore
)

# round all
# TODO: are digits for some columns needed?
for col in df_month.columns:
    df_month[col] = df_month[col].round(0)

# export month summary
df_month.to_csv(
    "out/month.tsv",
    sep="\t",
    lineterminator="\n",
)
df_month.to_excel("out/month.xlsx")
