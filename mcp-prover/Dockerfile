FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV ELAN_HOME=/root/.elan
ENV PATH=/root/.elan/bin:$PATH

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl git ca-certificates build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf \
    | sh -s -- -y --default-toolchain stable

COPY lakefile.lean lean-toolchain ./
COPY lean_proofs ./lean_proofs
RUN lake update && lake exe cache get

COPY . .

CMD ["python", "-m", "mcp_servers.mcp_prover_server"]
