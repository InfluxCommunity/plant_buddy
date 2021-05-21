# python:alpine is 3.{latest}
FROM python:buster 

RUN pip install flask
RUN pip install influxdb-client
RUN pip install matplotlib
RUN pip install mpld3

COPY src /app/

EXPOSE 5000
WORKDIR /app

ENTRYPOINT ["python", "app.py"]