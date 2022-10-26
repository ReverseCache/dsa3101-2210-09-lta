ARG CUDA_VER=11.5
ARG LINUX_VER=ubuntu20.04
ARG PYTHON_VER=3.9
ARG RAPIDS_VER=22.12
ARG FROM_IMAGE=rapidsai/rapidsai-core

FROM ${FROM_IMAGE}:${RAPIDS_VER}-cuda${CUDA_VER}-base-${LINUX_VER}-py${PYTHON_VER}

ARG RAPIDS_VER
ARG CUDA_VER

RUN apt-get update
RUN apt-get install -y python3-venv python3-pip

# RUN apt-get install nvidia-container-runtime

RUN gpuci_mamba_retry install -y -n rapids -c pytorch \
    "clx=${RAPIDS_VER}" \
    "cudatoolkit=${CUDA_VER}"

WORKDIR /usr/src/app

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt ./
RUN pip3 install requirements.txt

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