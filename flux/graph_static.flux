

from(bucket: "plantbuddy")
    |> range(start: -12h)
    |> filter(fn: (r) => r["_measurement"] == "sensor_data")
    |> filter(fn: (r) => r["device_id"] == "eui-323932326d306512" )
    |> filter(fn: (r) => r["_field"] == "soil_moisture")



