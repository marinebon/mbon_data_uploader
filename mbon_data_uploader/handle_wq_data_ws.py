"""
Script to upload water quality data into influxdb.

# Data quality checks:
=====================================================
## Data quality issues handled by the ingestion script:
1. `TIME` values set to `:` are replaced by empty string.
2. rows without `DATE` are dropped.
3. cell values "NA" and "ND" changed to empty

## manual changes I have made to the dataset before uploading
1. Time value '11:545' changed to '11:45'
2. semicolons in `TIME` column replaced with colons
3. 02/29/2019 (invalid date) replaced with 02/28/2019
4. replaced 0..07 with 0.07 in column "TURB-S"
=====================================================

Note that for some dates (< 1997) in the WS file there is no time value.
Without the time value the database will have duplicate points on those days.
This will mess up the display of the data; I think only one of the values on each day will be retained
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
    DBNAME = "fwc_coral_disease"  # TODO: this doesn't work?!? need to update the grafana db provissioning file
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

    NA_REP = -999.0  # influxdb doesn't handle NA, NaN, null

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

    for field_column in FIELDS:
        # change the few 'NA' values to empty cells
        dataframe[field_column].replace('NA', '', inplace=True)
        dataframe[field_column].replace('ND', '', inplace=True)

        # set na value on all empty cells
        dataframe[field_column].replace('', NA_REP, inplace=True)

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
        lambda d: int(d.timestamp())
    )
    filepath = f"{filepath}.csv"
    dataframe.to_csv(filepath, na_rep=NA_REP)

    # === submit to influxdb server
    logging.info("loading {}'s fields ({}) with tags={}".format(
        MEASUREMENT, FIELDS, TAGS
    ))

    # export_csv_to_influx --csv /tmp/WS_Aug_updated.xlsx.csv --dbname fwc_coral_disease --measurement Walton_Smith --field_columns 'NOX-S,NOX-B,NO3_S,NO3_B,NO2-S,NO2-B,NH4-S,NH4-B,TN-S,TN-B,DIN-S,DIN-B,TON-S,TON-B,TP-S,TP-B,SRP-S,SRP-B,APA-S,APA-B,CHLA-S,CHLA-B,TOC-S,TOC-B,SiO2-S,SiO2-B,TURB-S,TURB-B,SAL-S,SAL-B,TEMP-S,TEMP-B,DO-S,DO-B,Kd,pH,TN:TP,N:P,DIN:TP,Si:DIN,%SAT-S,%SAT_B,%Io,DSIGT' --tag_columns 'SURV,BASIN,SEGMENT,ZONE,STATION,SITE,LATDEC,LONDEC,DEPTH' --force_insert_even_csv_no_update True --server $INFLUXDB_HOSTNAME --time_column timestamp --force_float_columns 'NOX-S,NOX-B,NO3_S,NO3_B,NO2-S,NO2-B,NH4-S,NH4-B,TN-S,TN-B,DIN-S,DIN-B,TON-S,TON-B,TP-S,TP-B,SRP-S,SRP-B,APA-S,APA-B,CHLA-S,CHLA-B,TOC-S,TOC-B,SiO2-S,SiO2-B,TURB-S,TURB-B,SAL-S,SAL-B,TEMP-S,TEMP-B,DO-S,DO-B,Kd,pH,TN:TP,N:P,DIN:TP,Si:DIN,%SAT-S,%SAT_B,%Io,DSIGT'
    subprocess.run([
        "export_csv_to_influx",
        "--csv", filepath,
        "--dbname", DBNAME,
        "--measurement", MEASUREMENT,
        "--field_columns", ",".join(FIELDS),
        "--force_float_columns", ",".join(FIELDS),
        "--tag_columns", ','.join(TAGS),
        "--force_insert_even_csv_no_update", "True",
        "--server", INFLUXDB_SERVER,
        "--time_column", "timestamp"
    ], check=True)
