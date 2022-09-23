import "influxdata/influxdb/tasks"
option task = {
    name: "downsampled",
    every: 10m
}

from(bucket: "plantbuddy") 
    |> range(start: tasks.lastSuccess(orTime: -task.every))
    |> filter(fn: (r) => r._measurement == "sensor_data")
    |> aggregateWindow(every: 10m, fn: mean, createEmpty: false) 
    |> to(bucket: "downsampled")