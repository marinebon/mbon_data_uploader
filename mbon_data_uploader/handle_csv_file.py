import logging
import os
import pandas as pd
import subprocess


def handle_csv_file(filepath, form_args):
    """
    Pushes data from csv file into influxdb
    """
    INFLUXDB_SERVER = os.environ["INFLUXDB_HOSTNAME"]
    DBNAME = "fwc_coral_disease"

    assert ".csv" in filepath
    measurement = form_args["measurement"]
    assert measurement is not None
    tag_set = form_args["tag_set"]
    assert tag_set is not None
    fields = form_args['fields']
    assert fields is not None
    time_column = form_args['time_column']
    assert time_column is not None

    # === insert tag columns & set proper na values
    NA_REP = ''  # influxdb doesn't handle NA, NaN, null
    df = pd.read_csv(filepath)
    tag_columns = []
    for key_val in tag_set.split(','):
        key, val = key_val.split('=')
        df[key] = val
        tag_columns.append(key)
    df.to_csv(filepath, na_rep=NA_REP)

    # === submit to influxdb server
    logging.info("loading {}'s fields ({}) with tags={}".format(
        measurement, fields, tag_columns
    ))
    # measurement,tag_set      field_set
    # rs_oc_chlor,location=MIA anom,mean,clim
    subprocess.run([
        "export_csv_to_influx",
        "--csv", filepath,
        "--dbname", DBNAME,
        "--measurement", measurement,
        "--field_columns", fields,
        "--tag_columns", ','.join(tag_columns),
        "--force_insert_even_csv_no_update", "True",
        "--server", INFLUXDB_SERVER,
        "--time_column", time_column
    ], check=True)

    # === TODO: remove "na_rep" values from influx that were inserted by
    #           export_csv_to_influx
    # subprocess.run([
    #     "curl",
    #     "-G",
    #     INFLUXDB_SERVER + "/query",
    #     "--data-urlencode",
    #     "q=DELETE FROM " + DBNAME + " WHERE " + measurement + "==" + NA_REP,
    #     # "-u", "influx_user:influx_user_pw"
    # ], check=True)
