import pandas as pd
from pandas import DataFrame
import influxdb_client
import json


cloud_org = "05ea551cd21fb6e4"
cloud_bucket = "plantbuddy"

# Wrapper function used to query InfluxDB> Calls Flux scrip with paramaters. Data query to data frame.
def get_bucket_secret():
    # JSON file
    f = open ('/Users/jayclifford/Documents/repos/IoT_Plant_Demo/plant-buddy/src/secret/token.json', "r")
    dict = json.loads(f.read())

    return dict["token"]


client = influxdb_client.InfluxDBClient(
            url = "https://us-east-1-1.aws.cloud2.influxdata.com/",
            token = get_bucket_secret(),
            org = cloud_org,
            timeout = 30000)
query_api = client.query_api()

def querydata(bucket, measurment, field) -> DataFrame:
        params_dict = {"bucket": bucket, "measurments": measurment, "field":field }
        query = open("/Users/jayclifford/Documents/repos/IoT_Plant_Demo/plant-buddy/flux/paramaters.flux").read()
        result = query_api.query_data_frame(query, org=cloud_org, params=params_dict)


        return result

def check_alerts() -> DataFrame:
        query = open("/Users/jayclifford/Documents/repos/IoT_Plant_Demo/plant-buddy/flux/alerts.flux").read()
        result = query_api.query_data_frame(query, org=cloud_org)


        return result


if __name__ == "__main__":
  df = check_alerts()
  print(df)