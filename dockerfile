# python:alpine is 3.{latest}
FROM python:alpine 

RUN pip install flask
RUN pip install influxdb-client

COPY src /src/

EXPOSE 5000
WORKDIR /src

ENTRYPOINT ["python", "app.py"]