<h2 align="center">duetector🔍: Data Usage eBPF detector </h2>
<p align="center">
<a href="https://github.com/hitsz-ids/duetector/actions"><img alt="Actions Status" src="https://github.com/hitsz-ids/duetector/actions/workflows/python-package.yml/badge.svg"></a>
<a href="https://github.com/hitsz-ids/duetector/blob/main/LICENSE"><img alt="LICENSE" src="https://img.shields.io/github/license/hitsz-ids/duetector"></a>
<a href="https://github.com/hitsz-ids/duetector/releases/"><img alt="Releases" src="https://img.shields.io/github/v/release/hitsz-ids/duetector"></a>
<a href="https://github.com/hitsz-ids/duetector"><img alt="Last Commit" src="https://img.shields.io/github/last-commit/hitsz-ids/duetector"></a>
<a href="https://github.com/hitsz-ids/duetector"><img alt="Python version" src="https://img.shields.io/pypi/pyversions/duetector"></a>
</p>

<p align="center">
<a href="./README.md">中文</a> | <a href="./README_en.md">English</a>
</p>

## Introduction

> duetector is one of the components in the DataUCON project, which is designed to provide support for data usage control. [Intro DataUCON](https://dataucon.idslab.io/).

duetector🔍 is an eBPF-based data usage control probe that provides support for data usage control by probing for data usage behavior in the Linux kernel.

In the [ABAUC control model](https://github.com/hitsz-ids/dataucon), duetector can be used as a PIP (Policy Information Point) to obtain data usage behavior, so as to provide information about data usage behavior for PDP (Policy Decision Point). Provide information on data usage behavior to PDP (Policy Decision Point).

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
