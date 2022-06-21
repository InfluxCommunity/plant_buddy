# python:alpine is 3.{latest}
FROM python:3.9

RUN mkdir app 
WORKDIR /app
RUN mkdir app src flux
COPY docker/requirements.txt .
COPY ./src ./src
COPY ./flux ./flux


RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt




EXPOSE 5001
ENTRYPOINT ["python", "./src/app.py"]
