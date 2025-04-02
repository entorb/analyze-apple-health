#!/usr/bin/env python3
# by Dr. Torben Menke https://entorb.net
# https://github.com/entorb/analyze-apple-health
"""
Read Apple health exported data.

apple_health_export/export.xml
export in csv and Excel format
out/data-raw.*
Note: Excel has a limit of 1,048,576 rows...

based on https://towardsdatascience.com/analyse-your-health-with-python-and-apple-health-11c12894aae2
TODO: checkout export_cda.xml too
"""

import time
from pathlib import Path

import pandas as pd
from defusedxml.ElementTree import parse as XMLparse  # noqa: N812

Path("out").mkdir(exist_ok=True)

print("read xml data")
timelast = time.time()
tree = XMLparse("apple_health_export/export.xml")
# For every health record, extract the attributes into a dictionary (columns).
# Then create a list (rows).
root = tree.getroot()
record_list = [x.attrib for x in root.iter("Record")]
print(f"{int(time.time() - timelast)}s")


print("convert to DataFrame")
timelast = time.time()
# create DataFrame from a list (rows) of dictionaries (columns)
df = pd.DataFrame(record_list)
print(f"{int(time.time() - timelast)}s")


print("column modifications")
timelast = time.time()

df.index.name = "row"

# date fixes
for col in ["creationDate", "startDate", "endDate"]:
    # proper type to dates
    df[col] = pd.to_datetime(df[col])
    # Remove timezone from columns
    df[col] = df[col].dt.tz_localize(tz=None)

# convert value to numeric or NaN if fails
df["value"] = pd.to_numeric(df["value"], errors="coerce")

# how to treat nun-numeric values
# a ) filling with 1.0 (= one time) makes it easier to aggregate
# df["value"] = df["value"].fillna(1.0)
# b) just drop value=na rows
df = df[df["value"].notna()]

# shorter observation names: use vectorized replace function
df["type"] = df["type"].str.replace("HKQuantityTypeIdentifier", "")
df["type"] = df["type"].str.replace("HKCategoryTypeIdentifier", "")
print(f"{int(time.time() - timelast)}s")


print("export out/data-raw2.tsv")
timelast = time.time()
df.to_csv(
    "out/data-raw-2.tsv",
    sep="\t",
    lineterminator="\n",
)
print(f"{int(time.time() - timelast)}s")


if len(df.index) >= 1048576 - 1:
    print("too many rows for Excel export")
else:
    print("export out/data-raw-2.xlsx")
    timelast = time.time()
    df.to_excel("out/data-raw-2.xlsx")
    print(f"{int(time.time() - timelast)}s")
