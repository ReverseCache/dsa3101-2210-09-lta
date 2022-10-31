FROM ubuntu:latest
 
RUN apt-get update
RUN apt-get install -y python3-venv python3-pip

# RUN apt-get install nvidia-container-runtime

WORKDIR /usr/src/app

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY Frontend_api_calls.py ./
CMD ["python3" , "./Frontend_api_calls.py"]

#################//###########################
# RUN chmod -R ugo+w /opt/conda ${CLX_DIR} \
#     && conda clean -tipy \
#     && chmod -R ugo+w /opt/conda ${CLX_DIR}

# COPY entrypoint.sh /opt/docker/bin/entrypoint

# ENTRYPOINT [ "/opt/conda/bin/tini", "--", "/opt/docker/bin/entrypoint" ]

# CMD [ "/bin/bash" ]

#################//###########################