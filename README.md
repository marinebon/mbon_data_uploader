# mbon_data_uploader
Frontend for uploading mbon data into the mbon-in-a-box stack.
Flask app connects to influxdb and allows you to upload .csv files. 




## test csv uploading
```bash
export_csv_to_influx --csv /tmp/FKdbv2_Rrs_671_TS_VSNPP_daily_MIA_zeros.csv --dbname fwc_coral_disease --measurement demo --field_columns mean,climatology,anomaly --force_insert_even_csv_no_update True --server tylar-pc:8086 --time_column Time
```
