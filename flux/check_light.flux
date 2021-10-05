import "influxdata/influxdb/monitor"
import "influxdata/influxdb/v1"

option task = {name: "light check", every: 15, offset: 5s}

data = from(bucket: "plantbuddy")
    |> range(start: -10m)
    |> filter(fn: (r) => r._measurement == "light")
crit = (r) => r.reading > 1000
ok = (r) => r.reading <= 100
messageFn = (r) => "Room Light at ${string(v: r.reading)} for ${r.user}"
check = {
    _check_id: "check2light",
    _check_name: "light check",
    _type: "threshold",
    tags: {},
}

data
    |> v1["fieldsAsCols"]()
    |> yield()
    |> monitor.check(data: check, messageFn: messageFn, crit: crit, ok: ok)