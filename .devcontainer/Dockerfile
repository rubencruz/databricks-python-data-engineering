FROM python:3.12-slim

WORKDIR /workspace

RUN apt-get update && \
    apt-get install -y \
        git \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

#COPY requirements.txt .
COPY .devcontainer/requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ["bash"]