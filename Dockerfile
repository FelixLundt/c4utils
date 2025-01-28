FROM python:3.12-slim

WORKDIR /workspace

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir \
    pytest \
    pytest-watch \
    debugpy

# Install system dependencies including git, wget, and uidmap
RUN apt-get update && apt-get install -y \
    git \
    wget \
    uidmap \
    && rm -rf /var/lib/apt/lists/*

# Install Apptainer
RUN wget https://github.com/apptainer/apptainer/releases/download/v1.0.0/apptainer_1.0.0_amd64.deb && \
    apt-get update && \
    apt-get install -y ./apptainer_1.0.0_amd64.deb && \
    rm apptainer_1.0.0_amd64.deb

CMD ["tail", "-f", "/dev/null"]