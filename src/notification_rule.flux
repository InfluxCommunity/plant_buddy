package main

import "influxdata/influxdb/monitor"
import "slack"
import "influxdata/influxdb/secrets"
import "experimental"
import "http"

option task = {
    name: "SM Notification Rule",
    every: 1m,
    offset: 0s,
}

data = {
    _notification_rule_id: "notif-rule01xxxx",
    _notification_rule_name: "soil moisure crit",
    _notification_endpoint_id: "1234567890123456",
    _notification_endpoint_name: "soil moisture crit",
}
endpoint = http.endpoint(url: "http://71.126.178.222:5000/notify")
statuses = monitor["from"](start: -60m)
    |> filter(fn: (r) => r._level == "ok")
    // |> yield(name: "statuses")
    |> monitor.notify(
        data: data,
        endpoint: endpoint(
            mapFn: (r) => ({
                headers: {"Authorization":"Token 1234567890"},
                data: bytes(v: r._message),
            }),
        ),
    )
    |> yield(name: "monitor.notify")