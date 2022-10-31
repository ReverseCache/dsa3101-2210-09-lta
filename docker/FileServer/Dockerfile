FROM ubuntu:latest

RUN apt-get update
RUN apt-get install -y python3 python3-venv python3-pip

WORKDIR /usr/src/app

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY Messenger.py ./
COPY Fileserver.py ./
CMD ["python3" , "./Fileserver.py"] && ["python3" , "./Messenger.py"]