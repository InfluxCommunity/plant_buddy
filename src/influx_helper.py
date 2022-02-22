import secret_store
import influxdb_client
import pandas as pd
from pandas.core.frame import DataFrame

class influxHelper:
    def __init__(self, url, org, bucket) -> None:
        self.client = influxdb_client.InfluxDBClient(
            url = url,
            token = secret_store.get_bucket_secret(),
            org = org,
            timeout = 30000
    )

    
        self.cloud_bucket = bucket
        self.cloud_org = org
        # Ref to serial sensor samples. 
        self.sensor_names = {"LI":"light", "HU":"humidity", "ST":"soil_temp",
                "AT":"air_temp", "SM":"soil_moisture"}

        self.write_api = self.client.write_api()
        self.query_api = self.client.query_api()


    # The write to influx function formats the data point then writes to the database
    def write_to_influx(self,data):
        p = influxdb_client.Point(data["sensor_name"]).tag("user",data["user"]).tag("device_id",data["device"]).field("reading", int(data["value"]))
        self.write_api.write(bucket=self.cloud_bucket, org=self.cloud_org, record=p)
        print(p, flush=True)
        
    # The parse line function formats the data object
    def parse_line(self, line, user_name):
        data = {"device" : line[:2],
                "sensor_name" : self.sensor_names.get(line[2:4], "unkown"),
                "value" : line[4:],
                "user": user_name}
        return data

    # Getting our list of measurements for the dropdown in controls found in main_html.py
    def getMeasurements(self, bucket) -> list:
        measurments = []
        query = open("flux/measurments.flux").read().format(bucket)
        result = self.query_api.query(query, org=self.cloud_org)
        for table in result:
            for record in table:
                measurments.append(record["_value"])
        return measurments
    
    # Getting our list of buckets for the dropdown in controls found in main_html.py
    def getBuckets(self) -> list:
        buckets = []
        query = 'buckets()'
        result = self.query_api.query(query, org=self.cloud_org)
        for table in result:
            for record in table:
                buckets.append(record["name"])
        return buckets

    # Wrapper function used to query InfluxDB> Calls Flux script with paramaters. Data query to data frame.
    def querydata(self, bucket, measurment, field) -> DataFrame:
        query = open("flux/graph.flux").read().format(bucket, field, measurment)
        result = self.query_api.query_data_frame(query, org=self.cloud_org)
        return result
    
    # Wrapper function used to query InfluxDB> Calls Flux script with no paramaters.
    def querydataStatic(self) -> DataFrame:
        query = open("flux/graph_static.flux").read()
        result = self.query_api.query_data_frame(query, org=self.cloud_org)
        return result