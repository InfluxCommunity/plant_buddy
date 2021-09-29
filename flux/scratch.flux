from(bucket: "plantbuddy") 
    |> range(start: -48h)
    |> filter(fn: (r) => r.user == "{}}") 