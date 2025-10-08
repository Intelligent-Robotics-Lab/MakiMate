FROM ros:jazzy-ros-base
RUN apt-get update && apt-get install -y \
    python3-pip python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir pre-commit
WORKDIR /ws
