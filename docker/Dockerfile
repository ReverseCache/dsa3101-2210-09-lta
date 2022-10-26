FROM ubuntu:latest

RUN apt-get update
RUN apt-get install -y python3 python3-venv python3-pip

WORKDIR /usr/src/app

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip3 install requests 
RUN pip3 install pandas 

COPY pm25.py ./
CMD ["python3" , "./pm25.py"]

# COMMANDS TO RUN : 
# docker build -t mydocassign .
# docker run -v ${PWD}:/usr/src/app mydocassign 

# NOTE: if using windows cmd instead of powershell:
# run the following command instead as the second command:
# docker run -v %cd%:/usr/src/app mydocassign 