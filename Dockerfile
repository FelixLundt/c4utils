FROM python:3.12-slim

WORKDIR /workspace

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir \
    pytest \
    pytest-watch \
    debugpy

# Install system dependencies including git
RUN apt-get update && apt-get install -y \
    git \
    apptainer \
    && rm -rf /var/lib/apt/lists/*

CMD ["tail", "-f", "/dev/null"]