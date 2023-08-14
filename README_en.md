![](https://img.shields.io/github/license/hitsz-ids/duetector)
![](https://img.shields.io/github/v/release/hitsz-ids/duetector)
![](https://img.shields.io/pypi/dm/duetector)
![](https://img.shields.io/github/last-commit/hitsz-ids/duetector)
![](https://img.shields.io/pypi/pyversions/duetector)
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

[中文](README.md) | [English](README_en.md)

# duetector🔍: Data Usage eBPF detector

## Introduction

[Intro DataUCON project](https://dataucon.idslab.io/)

[DataUCON project docs](https://github.com/hitsz-ids/dataucon)

## Table of Contents

- [Features](#Features)
- [Installation](#Installation)
- [Quick Start](#quick-start)
- [API](#API)
- [Maintainers](#Maintainers)
- [contribute](#contribute)
- [License](#License)

## Feature

TBD

TODO: Features and corresponding [kernel config](https://github.com/iovisor/bcc/blob/master/docs/kernel_config.md)

## Installation

The code is distributed via Pypi, and you can install it with the following command

```bash
pip install duetector
```

Currently, the code relies on [BCC](https://github.com/iovisor/bcc) for on-the-fly compilation of eBPF code, we recommend [installing the latest BCC compiler](https://github.com/iovisor/bcc/blob/master/INSTALL.md)

Or use the Docker image that we provide

```bash
docker pull dataucon/duetector:latest
```

Pre-releases will not be updated on `latest`, you can specify the tag to pull, e.g. `v0.1.0`

```bash
docker pull dataucon/duetector:v0.1.0
```

## Quick start

TBD

## API documentation

TBD

## Maintainers

This project is initiated by **Institute of Data Security, Harbin Institute of Technology (Shen Zhen)**, if you are interested in this project and [DataUCON](https://dataucon.idslab.io/) project and willing to work together to improve it, welcome to join our open source community.

## How to contribute

You are very welcome to join! [Raise an Issue](https://github.com/hitsz-ids/duetector/issues/new) or submit a Pull Request.

Please refer to [Developer Documentation](./DEVELOP.md).

## License

This project uses Apache-2.0 license, please refer to [LICENSE](https://github.com/hitsz-ids/duetector/blob/main/LICENSE).
