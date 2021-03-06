# mbon_data_uploader
Frontend for uploading mbon data into the mbon-in-a-box stack.
Flask app connects to influxdb and allows you to upload .csv files.

## dev
1. clone repo
2. edit routes in `__init__.py`
3. run docker image
    * first time: `sudo docker build --tag mbon_data_uploader:0.0.1 . && sudo docker run --publish 5000:5000 --detach --name mbondatauploader mbon_data_uploader:0.0.1`
    * rebuild: `sudo docker build --tag mbon_data_uploader:0.0.1 . && sudo docker stop mbondatauploader && sudo docker rm mbondatauploader && sudo docker run --publish 5000:5000 --detach --name mbondatauploader mbon_data_uploader:0.0.1` 
4. view app @ localhost:5000/

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

SELECT mean("anomaly") AS anomaly FROM "modis_abi"
WHERE ("location" =~ /^$Locations$/) AND anomaly!=-999 AND $timeFilter
GROUP BY time($__interval) fill(null)

SELECT mean("anomaly") AS anomaly FROM "modis_abi"
WHERE ("location" =~ /^$Locations$/) AND anomaly!=-999 AND $timeFilter
GROUP BY time($__interval),"location" fill(null)
```

## prefilled GUI URL
The GUI is RESTful, meaning that you can create URLs pre-filled with your form information:
```
http://localhost:5000/?measurement=Rrs_671&tag_set=location=BIS,sensor=viirs&fields=mean,climatology,anomaly
```

## Submit data from CLI
Data can be submitted from the command line using curl:

```bash
curl -v \
--form "measurement=Rrs_671" \
--form 'tag_set="location=MIA,sensor=viirs"' \
--form 'fields="mean,climatology,anomaly"' \
--form 'file=@/home/tylar/Downloads/FKdbv2_Rrs_671_TS_VSNPP_daily_MIA.csv' \
--form 'time_column=Time' \
http://localhost:5000/
```

## troubleshooting
A server log is within the docker container in `~/mbon_data_uploader.log`.

500 errors should be displayed with the custom error html.
If an error like below is encountered:
```
Internal Server Error

The server encountered an unexpected internal server error

(generated by waitress)
```
This means the function which returns the 500 error page itself is broken.
