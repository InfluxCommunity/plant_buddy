# python:alpine is 3.{latest}
FROM python:alpine 

RUN pip install flask
RUN pip install influxdb-client

COPY src /app/

EXPOSE 5000
WORKDIR /app

ENTRYPOINT ["python", "app.py"]