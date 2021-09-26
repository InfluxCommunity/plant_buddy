from(bucket: "{}")
    |> range(start: -48h)
    |> filter(fn: (r) => r["_measurement"] == "{}")
    |> filter(fn: (r) => r["user"] == "{}")