FROM ubuntu:22.04

ARG BCC_VERSION

RUN apt-get update && apt-get install -y zip bison build-essential cmake flex git libedit-dev \
    libllvm14 llvm-14-dev libclang-14-dev python3 python3-pip python-is-python3 zlib1g-dev libelf-dev libfl-dev python3-setuptools \
    liblzma-dev libdebuginfod-dev arping netperf iperf \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 --branch ${BCC_VERSION} https://github.com/iovisor/bcc.git &&\
    mkdir bcc/build; cd bcc/build  &&\
    cmake .. &&\
    make -j$(nproc) &&\
    make install &&\
    cmake -DPYTHON_CMD=python3 .. # build python3 binding &&\
    pushd src/python/ &&\
    make &&\
    make install &&\
    popd

RUN pip install duetector --no-cache-dir
