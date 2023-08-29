ARG BCC_VERSION=v0.28.0

FROM dataucon/ubuntu-bcc:${BCC_VERSION}

ARG DUETECTOR_VERSION

RUN apt-get update && apt-get install -y tini \
    && rm -rf /var/lib/apt/lists/*
RUN pip install jupyterlab

RUN pip install duetector==${DUETECTOR_VERSION} --no-cache-dir


# Add application user

ARG APPLICATION_UID=9999
ARG APPLICATION_GID=9999
RUN addgroup --system --gid ${APPLICATION_GID} application && \
    adduser --system --gid ${APPLICATION_GID} --home /home/application --uid ${APPLICATION_UID} --disabled-password application && \
    usermod -s /bin/bash application

COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

CMD [ "/sbin/tini", "--" ]
ENTRYPOINT [ "/start.sh" ]
