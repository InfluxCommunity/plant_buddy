from(bucket: "plantbuddy")
    |> range(start: -24h)
    |> filter(fn: (r) => r["_measurement"] == "light")
    |> filter(fn: (r) => r["user"] == "jay")