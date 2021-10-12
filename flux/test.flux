import "array"

data = array.from(rows: [{_time: 2021-09-23T15:58:02.017Z, _value: 19.0},
{_time: 2020-09-23T15:48:02.017Z, _value: 16.0},
{_time: 2021-09-23T15:38:02.017Z, _value: 20.0},
{_time: 2021-09-23T15:28:02.017Z, _value: 20.0},
{_time: 2021-09-23T15:18:02.017Z, _value: 22.0},
{_time: 2021-09-23T15:08:02.017Z, _value: 7.0},
{_time: 2021-09-23T14:58:02.017Z, _value: 20.0},
{_time: 2021-09-23T14:48:02.017Z, _value: 19.0},
{_time: 2021-09-23T14:38:02.017Z, _value: 15.0},
{_time: 2021-09-23T14:28:02.017Z, _value: 19.0},
])
// |> yield(name: "data")
dueDate = 2021-09-23T14:28:02.017Z
data 
|> map(fn: (r) => ({ r with late: if r._time < dueDate then "true" else "false" }))
|> yield(name:"ontime")