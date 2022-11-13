FROM ubuntu:latest
 
RUN apt-get update
RUN apt-get install -y python3 python3-venv python3-pip

WORKDIR /usr/src/app

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY . ./
RUN pip3 install -r requirements.txt
RUN chmod a+x run.sh

CMD ["bash", "./run.sh"]
