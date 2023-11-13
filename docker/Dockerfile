ARG BCC_VERSION=v0.28.0

FROM python:3.10.12-slim-bookworm as builder

RUN pip install build twine hatch
COPY . /source
WORKDIR /source
RUN python -m build

FROM dataucon/ubuntu-bcc:${BCC_VERSION}

RUN apt-get update && apt-get install -y tini \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /source/dist/*.whl /tmp/
RUN pip install /tmp/*.whl --no-cache-dir

# Add application user
ARG APPLICATION_UID=9999
ARG APPLICATION_GID=9999
RUN addgroup --system --gid ${APPLICATION_GID} application && \
    adduser --system --gid ${APPLICATION_GID} --home /home/application --uid ${APPLICATION_UID} --disabled-password application && \
    usermod -s /bin/bash application
# Install Jupyterlab as example application
RUN pip install jupyterlab --no-cache-dir

COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

CMD [ "/sbin/tini", "--" ]
ENTRYPOINT [ "/start.sh" ]
