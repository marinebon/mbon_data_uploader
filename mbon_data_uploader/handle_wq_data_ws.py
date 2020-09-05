"""
Script to upload water quality data into influxdb.

# Data quality checks:
=====================================================
## Data quality issues handled by the ingestion script:
1. `TIME` values set to `:` are replaced by empty string.
2. rows without `DATE` are dropped.

## manual changes I have made to the dataset before uploading
1. Time value '11:545' changed to '11:45'
2. semicolons in `TIME` column replaced by colons
3. 02/29/2019 (invalid date) replaced with 02/28/2019
=====================================================
"""

import pytz
import dateutil
import logging
import numpy as np
import os
import pandas as pd
import subprocess


def handle_wq_data_ws(filepath, form_args):
    """
    Pushes data from water quality ws excel file into influxdb
    """
    assert ".xlsx" in filepath

    INFLUXDB_SERVER = os.environ["INFLUXDB_HOSTNAME"]
    DBNAME = "fk_water_quality"  # TODO: this doesn't work?!? need to update the grafana db provissioning file
    SHEET_NAME = "Data in ppm"
    MEASUREMENT = "Walton_Smith"
    TAGS = [    # metadata items attached to each measurment
        "SURV",
        "BASIN",
        "SEGMENT",
        "ZONE",
        "STATION",
        "SITE",
        "LATDEC",
        "LONDEC",
        "DEPTH",
    ]
    FIELDS = [
        "NOX-S", "NOX-B",
        "NO3_S", "NO3_B",
        "NO2-S", "NO2-B",
        "NH4-S", "NH4-B",
        "TN-S", "TN-B",
        "DIN-S", "DIN-B",
        "TON-S", "TON-B",
        "TP-S", "TP-B",
        "SRP-S", "SRP-B",
        "APA-S", "APA-B",
        "CHLA-S", "CHLA-B",
        "TOC-S", "TOC-B",
        "SiO2-S", "SiO2-B",
        "TURB-S", "TURB-B",
        "SAL-S", "SAL-B",
        "TEMP-S", "TEMP-B",
        "DO-S", "DO-B",
        "Kd",
        "pH",
        "TN:TP",
        "N:P",
        "DIN:TP",
        "Si:DIN",
        "%SAT-S", "%SAT_B",
        "%Io",
        "DSIGT"
    ]
    DATETIME = [
        "DATE",
        "TIME"
    ]
    NA_REP = ''  # influxdb doesn't handle NA, NaN, null

    dataframe = pd.read_excel(
        filepath,
        sheet_name=SHEET_NAME,
        header=0,
        parse_dates=DATETIME,
        na_filter=False
        # date_parser=lambda d0, d1: dateutil.parser.parse(f"{d0} {d1}")
    )
    # drop rows with no date
    dataframe["DATE"].replace('', np.nan, inplace=True)
    dataframe.dropna(subset=["DATE"], inplace=True)

    # fix the few columns with empty time but still have a colon
    dataframe["TIME"].replace(':', '', inplace=True)

    # combine date and time rows
    dataframe['date_time'] = dataframe.apply(
        lambda row: str(row["DATE"]).replace(
            "00:00:00",
            str(row["TIME"])
        ) if len(str(row["TIME"])) > 0 else str(row["DATE"]),
        axis=1
    )

    # clean up the datetime & add timezone
    timezone = pytz.timezone("US/Eastern")
    dataframe["date_time"] = dataframe["date_time"].apply(
        lambda d: timezone.localize(
            dateutil.parser.parse(d, ignoretz=True)
        )
    )

    # get timestamp from combined date and time
    dataframe["timestamp"] = dataframe["date_time"].apply(
        lambda d: d.timestamp()
    )
    filepath = f"{filepath}.csv"
    dataframe.to_csv(filepath, na_rep=NA_REP)

    # === submit to influxdb server
    logging.info("loading {}'s fields ({}) with tags={}".format(
        MEASUREMENT, FIELDS, TAGS
    ))
    subprocess.run([
        "export_csv_to_influx",
        "--csv", filepath,
        "--dbname", DBNAME,
        "--measurement", MEASUREMENT,
        "--field_columns", ",".join(FIELDS),
        "--tag_columns", ','.join(TAGS),
        "--force_insert_even_csv_no_update", "True",
        "--server", INFLUXDB_SERVER,
        "--time_column", "timestamp"
    ], check=True)
