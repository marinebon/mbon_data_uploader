import logging
import os
import pandas as pd
from io import StringIO
import subprocess

from mbon_data_uploader.strfy_subproc_error import subproc_error_wrapper

def handle_csv_file(filepath, form_args):
    """
    Pushes data from csv file into influxdb.
    Returns an html-formatted log file.
    """
    INFLUXDB_SERVER = os.environ["INFLUXDB_HOSTNAME"]
    DBNAME = "fwc_coral_disease"

    # === log setup
    log_stream = StringIO()
    logger = logging.getLogger("{}.{}".format(
        __name__,
        sys._getframe().f_code.co_name)
    )
    stream_handler = logging.StreamHandler(log_stream)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(
        logging.Formatter(
           '<pre>%(asctime)s|%(levelname)s\t|%(filename)s:%(lineno)s\t|%(message)s</pre>'
        )
    )
    logger.addHandler(stream_handler)

    # === basic sanity checks
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
    logger.info("loading {}'s fields ({}) with tags={}".format(
        measurement, fields, tag_columns
    ))
    # measurement,tag_set      field_set
    # rs_oc_chlor,location=MIA anom,mean,clim
    cmd_list = [
        "export_csv_to_influx",
        "--csv", filepath,
        "--dbname", DBNAME,
        "--measurement", measurement,
        "--field_columns", fields,
        "--tag_columns", ','.join(tag_columns),
        "--force_insert_even_csv_no_update", "True",
        "--server", INFLUXDB_SERVER,
        "--time_column", time_column
    ]
    logger.info(cmd_list)
    subproc_error_wrapper(cmd_list)
    
    return log_stream.getvalue()

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
