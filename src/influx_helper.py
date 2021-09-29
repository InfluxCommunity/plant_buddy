import secret_store
import influxdb_client
import pandas as pd
from pandas.core.frame import DataFrame

class influxHelper:
    def __init__(self, org, bucket) -> None:
        self.client = influxdb_client.InfluxDBClient(
            url = "https://us-east-1-1.aws.cloud2.influxdata.com/",
            token = secret_store.get_bucket_secret(),
            org = org
    )

    
        self.cloud_bucket = bucket
        self.cloud_org = org
        # Ref to serial sensor samples. 
        self.sensor_names = {"LI":"light", "HU":"humidity", "ST":"soil_temp",
                "AT":"air_temp", "SM":"soil_moisture"}

        self.write_api = self.client.write_api()
        self.query_api = self.client.query_api()



    def write_to_influx(self,data):
        p = influxdb_client.Point(data["sensor_name"]).tag("user",data["user"]).tag("device_id",data["device"]).field("reading", int(data["value"]))
        self.write_api.write(bucket=self.cloud_bucket, org=self.cloud_org, record=p)
        print(p, flush=True)

    def parse_line(self, line, user_name):
        data = {"device" : line[:2],
                "sensor_name" : self.sensor_names.get(line[2:4], "unkown"),
                "value" : line[4:],
                "user": user_name}
        return data

    def getMeasurements(self, bucket) -> list:
        measurments = []
        query = open("../flux/measurments.flux").read().format(bucket)
        result = self.query_api.query(query, org=self.cloud_org)
        for table in result:
            for record in table:
                measurments.append(record["_value"])
             
        
 
        return measurments
    
    def getBuckets(self) -> list:
        measurments = []
        query = 'buckets()'
        result = self.query_api.query(query, org=self.cloud_org)
        for table in result:
            for record in table:
                measurments.append(record["name"])
             
        
 
        return measurments

    


    # Wrapper function used to query InfluxDB> Calls Flux scrip with paramaters. Data query to data frame.
    def querydata(self, bucket, measurment, field) -> DataFrame:
        x_vals = []
        y_vals = []
        label = []
        query = open("../flux/graph.flux").read().format(bucket, measurment, field)
        result = self.query_api.query(query, org=self.cloud_org)
        for table in result:
                for record in table:
                    y_vals.append(record["_value"])
                    x_vals.append(record["_time"])
                    label = record["_measurement"]
        df = pd.DataFrame({
            "time": x_vals,
            "value": y_vals,
            "label": label
                })
        return df