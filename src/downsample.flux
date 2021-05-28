option task = {
    name: "downsampled",
    every: 10m
}
from(bucket: "plantbuddy") 
    |> range(start: -10m)
    |> aggregateWindow(every: 10m, fn: mean) 
    |> to(bucket: "downsampled")