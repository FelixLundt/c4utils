FROM python:3.12-slim

WORKDIR /agent

COPY examples/requirements.txt .
RUN pip install -r requirements.txt

# `examples` directory name must be changed to whatever the convention is going to be
# groups/agents need to have consistent names as a reference for the docker image, the
# directory for their code and for internal records.
# `agent_sandbox` directory name must be changed to wherever the c4utils package is
# the exact value of the timeout must be set somewhere and imported here. Maybe in some tournament config file?
COPY examples ./examples  
COPY agent_sandbox/timeout.py .
ENV PYTHONPATH=/agent

# Create wrapper script that applies the timeout decorator
RUN echo 'from timeout import with_timeout\n\
from examples import generate_move\n\
\n\
generate_move_with_timeout = with_timeout(generate_move)' > agent.py

