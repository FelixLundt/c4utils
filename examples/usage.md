The examples directory contains two agent definitions:

- `random_agent.py`: A random agent that makes moves at random.
- `fixed_time_agent.def`: A fixed-time agent that makes moves in a fixed amount of time (0.5 of the timeout).

They should be used in order to test the sandbox.

Locally:

- Build the container:
```bash
apptainer build --sandbox /tmp/agent_fixed_time/ ./agent_fixed_time.def
```
It was necessary to build the container in a sandbox and in the `\tmp` directory because of issue with the docker container running the development environment.

- Move it to the agents folder:
```bash
mv /tmp/agent_fixed_time/ /workspace/examples/agents/
mv /tmp/agent_fixed_time ./
```

- Run the tests.

