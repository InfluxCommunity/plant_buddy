// These variables will be added by the PlantBuddy app when making queries
// Uncomment the lines below to test the query directly
// _bucket = "plantbuddy"
// _sensor = "air_temperature"
// _device = "01"

from(bucket: _bucket)
    |> range(start: -24h)
    |> filter(fn: (r) => r["_measurement"] == "sensor_data")
    |> filter(fn: (r) => r["device_id"] == _device)
    |> filter(fn: (r) => r["_field"] == _sensor)



