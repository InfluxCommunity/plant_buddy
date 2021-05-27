from(bucket: "plantbuddy")
|> range(start: -48h)
|> last()