FROM python:3.8.6-slim

COPY ./requirements.txt /api/requirements.txt

WORKDIR /api

RUN pip3 install -r requirements.txt

COPY . /api

RUN mkdir templates

EXPOSE 5000

ENTRYPOINT ["uvicorn", "app.server:app", "--port" , "5000"]
