FROM ubuntu:18.04

COPY app /app

WORKDIR /app

RUN apt-get update &&  apt-get install -y \
    python3 \
    python3-pip

RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD ["python3", "app.py"]