# python:alpine is 3.{latest}
FROM python:alpine 

RUN pip install flask

COPY src /src/

EXPOSE 5000
WORKDIR /src

ENTRYPOINT ["python", "app.py"]