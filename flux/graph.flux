from(bucket: "{}")
    |> range(start: -24h)
    |> filter(fn: (r) => r["_measurement"] == "sensor_data")
    |> filter(fn: (r) => r["device_id"] == "{}")
    |> filter(fn: (r) => r["_field"] == "{}")



