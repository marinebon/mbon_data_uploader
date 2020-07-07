import pandas as pd
import subprocess


def handle_csv_file(filepath, form_args):
    """
    Pushes data from csv file into influxdb
    """
    assert ".csv" in filepath
    measurement = form_args["measurement"]
    assert measurement is not None
    tag_set = form_args["tag_set"]
    assert tag_set is not None

    # === insert tag columns & set proper na values
    df = pd.read_csv(filepath)
    tag_columns = []
    for key_val in tag_set.split(','):
        key, val = key_val.split('=')
        df[key] = val
        tag_columns.append(key)
    df.to_csv(filepath, na_rep="")  # TODO: influxdb expects ??? for na or NaN

    # === submit to influxdb server
    # measurement,tag_set      field_set
    # rs_oc_chlor,location=MIA anom,mean,clim
    subprocess.run([
        "export_csv_to_influx",
        "--csv", filepath,
        "--dbname", "fwc_coral_disease",
        "--measurement", measurement,
        "--field_columns", "mean,climatology,anomaly",
        "--tag_columns", ','.join(tag_columns),
        "--force_insert_even_csv_no_update", "True",
        "--server", "tylar-pc:8086",  # TODO: update this for prod
        "--time_column", "Time"
    ], check=True)
