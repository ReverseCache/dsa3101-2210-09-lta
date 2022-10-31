# YOLOv5 🚀 by Ultralytics, GPL-3.0 license
# Builds ultralytics/yolov5:latest-cpu image on DockerHub https://hub.docker.com/r/ultralytics/yolov5
# Image is CPU-optimized for ONNX, OpenVINO and PyTorch YOLOv5 deployments

# Start FROM Ubuntu image https://hub.docker.com/_/ubuntu
FROM ubuntu:latest

# Install linux packages
RUN apt-get update
RUN apt-get install -y python3 python3-venv python3-pip
# libgl1-mesa-glx libglib2.0-0 libpython3.8-dev
# RUN alias python=python3

# Create working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install pip packages
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy contents
# COPY . /usr/src/app  (issues as not a .git directory)
COPY model ./
COPY yolov5 ./
COPY main.py ./
COPY segmentation.py ./

CMD ["python3" , "./main.py"]
# Usage Examples -------------------------------------------------------------------------------------------------------

# Build and Push
# t=ultralytics/yolov5:latest-cpu && sudo docker build -f utils/docker/Dockerfile-cpu -t $t . && sudo docker push $t

# Pull and Run
# t=ultralytics/yolov5:latest-cpu && sudo docker pull $t && sudo docker run -it --ipc=host -v "$(pwd)"/datasets:/usr/src/datasets $t