FROM python:3.7.2-slim

COPY ./requirements.txt /api/requirements.txt

WORKDIR /api

RUN pip3 install -r requirements.txt

COPY . /api

EXPOSE 5000

ENTRYPOINT ["python3.7", "start.py", "5000"]
