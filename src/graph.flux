from(bucket: "plantbuddy")
    |> range(start: -24h)
    |> aggregateWindow(every: 10m, fn: mean )
  