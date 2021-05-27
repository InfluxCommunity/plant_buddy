import "influxdata/influxdb/monitor"
import "influxdata/influxdb/v1"


data = from(bucket: "plantbuddy")
    |> range(start: -10m)
    |> filter(fn: (r) => r._measurement == "soil_moisture")


option task = {name: "soil moisture check", every: 10m, offset: 0s}

check = {_check_id: "check1xxxxxxxxxx",
        _check_name: "soil moisture check",
        _type: "threshold",
        tags: {}
}

ok = (r) => r.reading > 35
crit = (r) => r.reading <= 35

messageFn = (r) => "soil moisture at ${string(v:r.reading)} for ${r.user}"

data
    |> v1["fieldsAsCols"]()
    |> yield()
    |> monitor.check(data: check, messageFn: messageFn, crit: crit, ok: ok)
