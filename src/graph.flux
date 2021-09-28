from(bucket: "{}")
    |> range(start: -24h)
    |> filter(fn: (r) => r["_measurement"] == "{}")
    |> filter(fn: (r) => r["user"] == "{}")