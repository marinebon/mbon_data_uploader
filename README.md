# mbon_data_uploader
Frontend for uploading mbon data into the mbon-in-a-box stack.
Flask app connects to influxdb and allows you to upload .csv files.

## test csv uploading
```bash
export_csv_to_influx --csv /tmp/FKdbv2_Rrs_671_TS_VSNPP_daily_MIA_zeros.csv --dbname fwc_coral_disease --measurement demo --field_columns mean,climatology,anomaly --force_insert_even_csv_no_update True --server tylar-pc:8086 --time_column Time
```

## dealing with NA values
The ExportCsvToInflux script inserts a value representing empty field values.
By default the NA value representation is -999.
I've tried modifying the source and following up with a `DELETE`, but in short:
there isn't an easy way to fix this.
The best we can do is filter out the NA values in our queries.
It's easiest to use the grafana "text edit mode" for the query.
The query should look something like the following examples:
```
SELECT mean("anomaly") FROM "rs_chlora" WHERE "anomaly"!=-999 AND $timeFilter GROUP BY time($__interval)

SELECT mean("anomaly") FROM "rs_oc_chlor" WHERE ("location" =~ /^$Locations$/) AND anomaly!=-999 AND $timeFilter GROUP BY time($__interval) fill(null)
```

## Submit data from CLI
Data can be submitted from the command line using curl

```bash

```
