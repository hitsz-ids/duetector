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

**🐛🐞🧪 The project is under heavy development, looking forward to any bug reports, feature requests, pull requests!**

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

- [X] Plug-in system
  - [X] Customized tracer support
  - [X] Support for custom filters
  - [X] Custom collector support
  - [X] [Custom Plugin Examples](./examples/)
- [ ] Configuration Management
  - [X] Configuration using a single configuration file
  - [X] Generate Plugin Configuration
  - [ ] Support for dynamically loading configurations
- [ ] eBPF-based data usage probes
  - [X] File Open Operation
  - [ ] ......
- [X] Data collector with SQL database support
- [X] CLI Tools
- [ ] PIP Service

The eBPF probe requires kernel support, see [Kernel Support](./docs/kernel_config.md)

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

Pre-releases will not be updated to `latest`, you can specify the tag to pull, e.g. `v0.0.1a`

```bash
docker pull dataucon/duetector:v0.0.1a
```

For more details on running with docker images see [here](./docs/how-to/run-with-docker.md)

## Quick start

Start monitor using the command line, since bcc requires root privileges, we use the `sudo` command, which will start all probes and collect the probes into the `duetector-dbcollector.sqlite3` file in the current directory

```bash
sudo duectl start
```

Press `CRTL+C` to exit monitoring and you will see a summary output on the screen

```
{'DBCollector': {'OpenTracer': {'count': 31, 'first at': 249920233249912, 'last': Tracking(tracer='OpenTracer', pid=641616, uid=1000, gid= 1000, comm='node', cwd=None, fname='SOME-FILE', timestamp=249923762308577, extended={})}}}
```

At startup, the configuration file will be automatically generated at `~/.config/duetector`, and you can specify the configuration file to use with `--config`.

```bash
sudo duectl start --config <config-file-path
```

When using a plugin, the default configuration file will not contain the plugin's configuration, use the dynamically-generated configuration directive to generate a configuration file with the plugin's configuration, this directive also supports merging existing configuration files and environment variables.

```bash
duectl generate-dynamic-config --help
```

Use `generate-config` to restore the default state in case of configuration file errors.

```bash
duectl generate-config
```

More documentation and examples can be found [here](. /docs/).

## API documentation

WIP

## Maintainers

This project is initiated by **Institute of Data Security, Harbin Institute of Technology (Shen Zhen)**, if you are interested in this project and [DataUCON](https://dataucon.idslab.io/) project and willing to work together to improve it, welcome to join our open source community.

## How to contribute

You are very welcome to join! [Raise an Issue](https://github.com/hitsz-ids/duetector/issues/new) or submit a Pull Request.

Please refer to the [Developer Documentation](./CONTRIBUTING.md).

Learn about the design ideas and architecture of this project here: [DESIGN DOCUMENTS](./docs/design/README.md).

## License

This project uses Apache-2.0 license, please refer to [LICENSE](https://github.com/hitsz-ids/duetector/blob/main/LICENSE).
