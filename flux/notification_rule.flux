import "influxdata/influxdb/monitor"
import "influxdata/influxdb/secrets"
import "http"

option task = {
    name: "SM Notification Rule",
    every: 1m,
    offset: 0s,
}

rule = {
    _notification_rule_id: "notif-rule01xxxx",
    _notification_rule_name: "soil moisture crit",
    _notification_endpoint_id: "1234567890123456",
    _notification_endpoint_name: "soil moisture crit",
}
endpoint = http.endpoint(url: "http://71.126.178.222:5000/notify")
monitor.from(start: -2m)
    |> filter(fn: (r) => r._level == "crit")
    |> monitor.notify(
        data: rule,
        endpoint: endpoint(
            mapFn: (r) => ({
                headers: {"Authorization":secrets.get(key: "pb_secret")},
                data: bytes(v: r._message),
            }),
        ),
    )
    |> yield(name: "monitor.notify")