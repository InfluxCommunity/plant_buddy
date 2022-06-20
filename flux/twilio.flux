import "strings"
import "regexp"
import "json"
import "influxdata/influxdb/secrets"
import "influxdata/influxdb/schema"
import "influxdata/influxdb/monitor"
import "http"
import "experimental"
import "influxdata/influxdb/tasks"

option task = {name: "Twilio Moisture Check", every: 10m, offset: 0s}


check = {_check_id: "056gme999b22", _check_name: "Twilio Alert", _type: "custom", tags: {}}
notification = {
    _notification_rule_id: "056gme999b22",
    _notification_rule_name: "Twilio Alert Rule",
    _notification_endpoint_id: "056gme999b22",
    _notification_endpoint_name: "Twilio Alert Endpoint",
}

task_data =
    from(bucket: "plantbuddy")
        |> range(start: tasks.lastSuccess(orTime: -1h))
        |> filter(fn: (r) => r["_measurement"] == "sensor_data")
        |> filter(fn: (r) => r["_field"] == "soil_moisture")
trigger = (r) => r["soil_moisture"] < 30
messageFn = (r) =>
    " ${time(v: r._source_timestamp)} Your plant is getting thirsty. Moisture Level is at: ${r.soil_moisture}% !"

username = secrets.get(key: "twilio_username")
password = secrets.get(key: "twilio_password")
auth = http.basicAuth(u: username, p: password)

task_data
    |> schema["fieldsAsCols"]()
    |> filter(fn: (r) => r["_measurement"] == "sensor_data")
    |> monitor["check"](data: check, messageFn: messageFn, crit: trigger)
    |> filter(fn: trigger)
    |> limit(n: 1, offset: 0)
    |> yield(name: "notify")
    |> monitor["notify"](
        data: notification,
        endpoint:
            http.endpoint(
                url: "https://api.twilio.com/2010-04-01/Accounts/<INSERT_TWILIO_ACCOUNT>/Messages.json",
            )(
                mapFn: (r) => {
                    body = r._message

                    return {
                        headers: {"Content-Type": "application/x-www-form-urlencoded", Authorization: auth},
                        data: bytes(v: "To=########&From=#######&Body="+ body) ,
                    }
                },
            ),
    )