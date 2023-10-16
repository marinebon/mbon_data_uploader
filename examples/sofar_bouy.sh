#!/bin/bash
# submits a sofar .csv to mbon_data_uploader
#
# example buoy csv head from api.sofarocean.com/fetch/download-sensor-data/?spotterId=SPOT-30987C
# ```
# utc_timestamp,latitude,longitude,sensor_position,bristlemouth_node_id,data_type,units,value
# 2023-07-01T03:51:25.000Z,27.9074167,-93.5983167,1,,sofar_temperature,°C,30.78
# 2023-07-01T03:51:25.000Z,27.9074167,-93.5983167,2,,sofar_temperature,°C,29.480000000000004
# 2023-07-01T03:46:25.000Z,27.9074,-93.5983167,1,,sofar_temperature,°C,30.78
# ```


UPLOADER_HOSTNAME='http://tylar-pc:5000'
UPLOADER_ROUTE=$UPLOADER_HOSTNAME/submit/sat_image_extraction
FILEPATH=TODO
BOUY_ID=SPOT30987C

# TODO: must convert utc_timestamp to unix time?
# TODO: should be tag_set=location=$BOUY_ID ?

curl \
    --form measurement=sofar_bouy \
    --form tag_set=spotter_id=$BOUY_ID \
    --form fields=value,sensor_position \
    --form file=@$FILEPATH \
    --form time_column=utc_timestamp \
    $UPLOADER_ROUTE
