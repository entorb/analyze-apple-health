#!/usr/bin/env python3
# by Dr. Torben Menke https://entorb.net
# https://github.com/entorb/analyze-apple-health

"""
read Apple health exported data from
apple_health_export/export.xml
export in csv and Excel format
out/data-raw.*
Note: Excel has a limit of 1,048,576 rows...

TODO: checkout export_cda.xml as well
"""

# based on https://towardsdatascience.com/analyse-your-health-with-python-and-apple-health-11c12894aae2


# requirements:
# pip3 install pandas

# import numpy as np
import os
import pandas as pd
import time
import xml.etree.ElementTree as ET


os.makedirs("out", exist_ok=True)


print("read xml data")
timelast = time.time()
# create element tree object
tree = ET.parse("apple_health_export/export.xml")
# for every health record, extract the attributes into a dictionary (columns). Then create a list (rows).
root = tree.getroot()
record_list = [x.attrib for x in root.iter("Record")]
print("%ds" % (time.time() - timelast))


print("convert to DataFrame")
timelast = time.time()
# create DataFrame from a list (rows) of dictionaries (columns)
df = pd.DataFrame(record_list)
print("%ds" % (time.time() - timelast))


# print("export out/data-raw-1.tsv")
# timelast = time.time()
# df.to_csv(
#     "out/data-raw-1.tsv",
#     sep="\t",
#     line_terminator="\n",
# )
# print("%ds" % (time.time() - timelast))


print("column modifications")
timelast = time.time()

df.index.name = "row"

# date fixes
for col in ["creationDate", "startDate", "endDate"]:
    # proper type to dates
    df[col] = pd.to_datetime(df[col])
    # Remove timezone from columns
    df[col] = df[col].dt.tz_localize(tz=None)

# value is numeric, NaN if fails
df["value"] = pd.to_numeric(df["value"], errors="coerce")

# some records do not measure anything, just count occurences
# filling with 1.0 (= one time) makes it easier to aggregate
df["value"] = df["value"].fillna(1.0)

# shorter observation names: use vectorized replace function
df["type"] = df["type"].str.replace("HKQuantityTypeIdentifier", "")
df["type"] = df["type"].str.replace("HKCategoryTypeIdentifier", "")
print("%ds" % (time.time() - timelast))


print("export out/data-raw2.tsv")
timelast = time.time()
df.to_csv(
    "out/data-raw-2.tsv",
    sep="\t",
    line_terminator="\n",
)
print("%ds" % (time.time() - timelast))


if len(df.index) >= 1048576 - 1:
    print("too many rows for Excel export")
else:
    print("export out/data-raw-2.xlsx")
    timelast = time.time()
    df.to_excel("out/data-raw-2.xlsx")
    print("%ds" % (time.time() - timelast))
