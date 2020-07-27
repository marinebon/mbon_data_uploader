import os
import shutil


def handle_worldview_image(filepath, form_args):
    """
    Pushes data from csv file into influxdb
    """
    POSTGIS_SERVER = os.environ["POSTGIS_SERVER"]
    DBNAME = "fwc_coral_disease"

    assert ".tif" in filepath
    product_type = form_args["product_type"]
    assert product_type is not None
    region_name = form_args["region_name"]
    assert region_name is not None

    # === put file into filesystem imars-objects
    fname = os.path.basename(filepath)
    new_filepath = f"/srv/imars-objects/{region_name}/{product_type}/{fname}"
    # cp filepath new_filepath
    shutil.move(filepath, new_filepath)

    # === insert file metadata into database
    # TODO
    raise NotImplementedError("NYI")
