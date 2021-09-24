from(bucket: "plantbuddy")
    |> range(start: -48h)
    |> filter(fn: (r) => r.user == "{}" )
    |> filter(fn: (r) => r["_measurement"] == "soil_moisture")