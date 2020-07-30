import os
import shutil

import psycopg2


def handle_worldview_image(filepath, form_args):
    """
    Pushes data from csv file into influxdb
    """
    POSTGIS_HOSTNAME = os.environ["POSTGIS_HOSTNAME"]
    POSTGRES_USER = os.environ["POSTGRES_USER"]
    POSTGRES_PASS = os.environ["POSTGRES_PASS"]
    POSTGRES_DB = os.environ["POSTGRES_DB"]
    POSTGRES_PORT = os.environ["POSTGRES_PORT"]
    SCHEMA_NAME = os.environ["SCHEMA_NAME"]
    TABLE_NAME = os.environ["TABLE_NAME"]

    conn = psycopg2.connect(
        host=POSTGIS_HOSTNAME,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASS,
        port=POSTGRES_PORT
    )
    curs = conn.cursor()

    assert ".tif" in filepath
    product_type = form_args["product_type"]
    assert product_type is not None
    region_name = form_args["region_name"]
    assert region_name is not None

    # === insert file metadata into database
    curs.execute(
        f"""
        INSERT INTO {SCHEMA_NAME}.{TABLE_NAME} (coltest) VALUES ('Itwk!');
        """
    )

    # === put file into filesystem imars-objects
    fname = os.path.basename(filepath)
    new_filepath = f"/srv/imars-objects/{region_name}/{product_type}/{fname}"
    # cp filepath new_filepath
    shutil.move(filepath, new_filepath)
