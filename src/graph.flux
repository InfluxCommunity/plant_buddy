from(bucket: "downsampled")
    |> range(start: -48h)
    |> filter(fn: (r) => r.user == "{}" )
  