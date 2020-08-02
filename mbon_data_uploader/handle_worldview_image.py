import os
import shutil
import subprocess
import sys

from filepanther.filepath_to_metadata import filepath_to_metadata
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

    # format filepath using result from
    try:
        curs.execute(
            f"""
            SELECT path_format_str FROM {SCHEMA_NAME}.products
            WHERE short_name = '{product_type}';
            """
        )
    except psycopg2.errors.UndefinedColumn as err:
        # add more detail to error message:
        raise (
            type(err)(
                str(err) + "\n Given product type is not valid."
            ).with_traceback(sys.exc_info()[2])
        )

    product_format_str = curs.fetchone()[0]

    # === collect metadata from filepath
    metadata_dict = filepath_to_metadata(
        product_format_str, filepath, basename_only=True
    )
    # === combine with metadata from the form
    metadata_dict.update({  # TODO: check for unequal vals instead of update
        "product_short_name": product_type,
        "area_short_name": region_name,
        "multihash": _get_base58_multihash(filepath),
        "n_bytes": os.path.getsize(filepath),
    })

    # === figure out new filepath where the file will be stored
    fname = os.path.basename(filepath)
    new_filepath = (
        f"/srv/imars-objects/{metadata_dict['product_short_name']}/"
        f"{metadata_dict['area_short_name']}/"
        f"{fname}"
    )
    metadata_dict["filepath"] = new_filepath

    # === insert file metadata into database
    curs.execute(
        f"""
        INSERT INTO {SCHEMA_NAME}.{TABLE_NAME}
        (
            filepath,multihash,provenance,date_time,last_processed,
            n_bytes,product_name,area_name,status
        )
        VALUES
        (
            '{metadata_dict['filepath']}',
            '{metadata_dict['multihash']}',
            'web_submit',
            '{metadata_dict['_datetime']}',
            '1901-01-01 01:01:01',
            {metadata_dict['n_bytes']},
            '{metadata_dict['product_short_name']}',
            '{metadata_dict['area_short_name']}',
            'new'
        );
        """
    )

    # === put file into filesystem imars-objects
    # cp filepath new_filepath
    shutil.move(filepath, new_filepath)

    # finalize db connection
    conn.commit()
    conn.close()


def _get_base58_multihash(filepath):
    # === FAILED attempt to create ipfs-style multihash:
    # # TODO: could better handle big files see
    # # https://www.quickprogrammingtips.com/python/
    # #     how-to-calculate-sha256-hash-of-a-file-in-python.html
    # with open(filepath, "rb") as fileobj:
    #     bytes = fileobj.read()
    #     hash = hashlib.sha256(bytes).hexdigest()  # raw bytes
    #     multihash = "1220" + hash
    #     return b58_multihash = base58.b58encode(bytes.fromhex(multihash))

    # so let's just use ipfs:
    _gethash_ipfs(filepath)


def _gethash_ipfs(filepath):
    """
    Get hash using IPFS system call.
    IPFS must be installed for this to work.
    """
    return subprocess.check_output([
        'ipfs', 'add',
        '-Q',  # --quieter    bool - Write only final hash
        '-n',  # --only-hash  bool - Only chunk and hash; do not write to disk
        filepath
    ]).strip().decode('utf-8')
