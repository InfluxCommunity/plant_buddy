option task = {
    name: "downsampled",
    every: 10m
}
from(bucket: "plantbuddy")
    |> range(start: -0)
    |> aggregateWindow(every: 10m, fn: mean )
    |> to(bucket: "downsampled")
  