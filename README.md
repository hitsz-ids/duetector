<h2 align="center">duetector🔍: Data Usage Extensible detector(eBPF Support)</h2>
<p align="center">
<a href="https://github.com/hitsz-ids/duetector/actions"><img alt="Actions Status" src="https://github.com/hitsz-ids/duetector/actions/workflows/python-package.yml/badge.svg"></a>
<a href='https://duetector.readthedocs.io/en/latest/?badge=latest'><img src='https://readthedocs.org/projects/duetector/badge/?version=latest' alt='Documentation Status' /></a>
<a href="https://results.pre-commit.ci/latest/github/hitsz-ids/duetector/main"><img alt="pre-commit.ci status" src="https://results.pre-commit.ci/badge/github/hitsz-ids/duetector/main.svg"></a>
<a href="https://github.com/hitsz-ids/duetector/blob/main/LICENSE"><img alt="LICENSE" src="https://img.shields.io/github/license/hitsz-ids/duetector"></a>
<a href="https://github.com/hitsz-ids/duetector/releases/"><img alt="Releases" src="https://img.shields.io/github/v/release/hitsz-ids/duetector"></a>
<a href="https://github.com/hitsz-ids/duetector/releases/"><img alt="Pre Releases" src="https://img.shields.io/github/v/release/hitsz-ids/duetector?include_prereleases&label=pre-release&logo=github"></a>
<a href="https://github.com/hitsz-ids/duetector"><img alt="Last Commit" src="https://img.shields.io/github/last-commit/hitsz-ids/duetector"></a>
<a href="https://github.com/hitsz-ids/duetector"><img alt="Python version" src="https://img.shields.io/pypi/pyversions/duetector"></a>
<a href="https://github.com/hitsz-ids/duetector/contributors"><img alt="contributors" src="https://img.shields.io/github/all-contributors/hitsz-ids/duetector?color=ee8449&style=flat-square"></a>
</p>

<p align="center">
 <a href="./README.md">English</a> | <a href="./README_zh.md">中文</a>
</p>

## Introduction

> duetector is one of the components in the DataUCON project, which is designed to provide support for data usage control. [Intro DataUCON](https://dataucon.idslab.io/).

duetector🔍 is an extensible data usage control detector that provides support for data usage control by probing for data usage behavior in the Linux kernel(based on eBPF).

**🐛🐞🧪 The project is under heavy development, looking forward to any bug reports, feature requests, pull requests!**

In the [ABAUC control model](https://github.com/hitsz-ids/dataucon), duetector can be used as a PIP (Policy Information Point) to obtain data usage behavior, so as to provide information about data usage behavior for PDP (Policy Decision Point). Provide information on data usage behavior to PDP (Policy Decision Point).

## Table of Contents

- [Features](#Features)
- [Installation](#Installation)
- [Quick Start](#quick-start)
- [API](#API-documentation)
- [Maintainers](#Maintainers)
- [Contributors](#Contributors)
- [How to contribute](#How-to-contribute)
- [License](#License)

## Feature

- Plug-in system support, see [examples](./examples/) for more details
  - [X] Custom `Tracer` and `TracerManager`
  - [X] Custom `Filters` and `FilterManager`
  - [X] Custom `Collector` and `CollectorManager`
  - [X] Custom `Analyzer` and `AnalyzerManager`
- Configuration Management
  - [X] Configuration using a single configuration file
  - [X] Generate Plugin Configuration
  - [ ] Support for dynamically loading configurations
- `Tracer` Support
  - [X] eBPF-based tracer
  - [X] Shell command tracer
  - [ ] Subprocess tracer
- `Filter` Support
  - [X] Pattern matching, based on regular expressions
- `Collector` and `Analyzer` Support
  - [X] SQL database
  - [ ] Opentelemetry
- Analyzer Support
  - [X] SQL database support
  - [ ] Opentelemetry support
- User Interface
  - [X] CLI Tools
  - [X] PIP Service
  - [ ] Control Panel
- Enhancements
  - [ ] Runc containers identification

The eBPF program requires kernel support, see [Kernel Support](./docs/kernel_config.md)

## Installation

The code is distributed via Pypi, and you can install it with the following command

```bash
pip install duetector
```

Currently, the code relies on [BCC](https://github.com/iovisor/bcc) for on-the-fly compilation of eBPF code, we recommend [installing the latest BCC compiler](https://github.com/iovisor/bcc/blob/master/INSTALL.md)

Or use the Docker image that we provide, which uses [JupyterLab](https://github.com/jupyterlab/jupyterlab) as the **example** user application, or you can modify the [Dockerfile](./docker/Dockerfile) and [startup script](./docker/start.sh) to customize the user application.

```bash
docker pull dataucon/duetector:latest
```

Pre-releases will not be updated to `latest`, you can specify the tag to pull, e.g. `v0.0.1a`

```bash
docker pull dataucon/duetector:v0.0.1a
```

For more details on running with docker images see [here](./docs/how-to/run-with-docker.md)

## Quick start

> More documentation and examples can be found [here](. /docs/).

### Start detector

Start monitor using the command line, since bcc requires root privileges, we use the `sudo` command, which will start all probes and collect the probes into the `duetector-dbcollector.sqlite3` file in the current directory

```bash
sudo duectl start
```

Press `CRTL+C` to exit monitoring and you will see a summary output on the screen

```
{'DBCollector': {'OpenTracer': {'count': 31, 'first at': 249920233249912, 'last': Tracking(tracer='OpenTracer', pid=641616, uid=1000, gid= 1000, comm='node', cwd=None, fname='SOME-FILE', timestamp=249923762308577, extended={})}}}
```

Enable `DEBUG` log

```bash
sudo DUETECTOR_LOG_LEVEL=DEBUG duectl start
```

At startup, the configuration file will be automatically generated at `~/.config/duetector`, and you can specify the configuration file to use with `--config`.

```bash
sudo duectl start --config <config-file-path>
```

Configuration using environment variables is also supported:

```bash
Usage: duectl start [OPTIONS]

  Start A bcc monitor and wait for KeyboardInterrupt

Options:
  ...
  --load_env BOOLEAN            Weather load env variables,Prefix: DUETECTOR_,
                                Separator:__, e.g. DUETECTOR_config__a means
                                config.a, default: True
  ...
```


When using a plugin, the default configuration file will not contain the plugin's configuration, use the dynamically-generated configuration directive to generate a configuration file with the plugin's configuration, this directive also supports merging existing configuration files and environment variables.

```bash
duectl generate-dynamic-config --help
```

Use `generate-config` to restore the default state in case of configuration file errors.

```bash
duectl generate-config
```

Going a step further, running in the background you can use the `duectl-daemon start` command, which will run a daemon in the background, which you can stop using `duectl-daemon stop`

Use `duectl-daemon --help` for more details:

```bash
Usage: duectl-daemon [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  start   Start a background process of command `duectl start`.
  status  Show status of process.
  stop    Stop the process.
```

### Analyzing with analyzer

We provide an [Analyzer](https://duetector.readthedocs.io/en/latest/analyzer/index.html) that can query the data in storage, try it in [user case](./docs/usercases/simplest-open-count/README.md)

### Using duetector server

We provide a Duetector Server as an external PIP service and control interface

A Duetector Server can be started using `duectl-server` and will listen on `0.0.0.0:8120` by default, you can modify it using `--host` and `--port`.

```bash
$ duectl-server start --help
Usage: duectl-server start [OPTIONS]

  Start duetector server

Options:
  --config TEXT       Config file path, default:
                      ``~/.config/duetector/config.toml``.
  --load_env BOOLEAN  Weather load env variables, Prefix: ``DUETECTOR_``,
                      Separator:``__``, e.g. ``DUETECTOR_config__a`` means
                      ``config.a``, default: True
  --workdir TEXT      Working directory, default: ``.``.
  --host TEXT         Host to listen, default: ``0.0.0.0``.
  --port INTEGER      Port to listen, default: ``8120``.
  --workers INTEGER   Number of worker processes, default: ``1``.
  --help              Show this message and exit.
```

After the service has started, visit `http://{ip}:{port}/docs` to see the API documentation.

Similarly, using `duectl-server-daemon start` you can run a Duetector Server in the background, and you can stop it using `duectl-server-daemon stop`

```bash
$ duectl-server-daemon
Usage: duectl-server-daemon [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  start   Start a background process of command ``duectl-server start``.
  status  Show status of process.
  stop    Stop the process.
```

## API documentation

See [docs of duetector](https://duetector.readthedocs.io/)

## Maintainers

This project is initiated by **Institute of Data Security, Harbin Institute of Technology (Shen Zhen)**, if you are interested in this project and [DataUCON](https://dataucon.idslab.io/) project and willing to work together to improve it, welcome to join our open source community.

## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/wunder957"><img src="https://avatars.githubusercontent.com/u/141890183?v=4?s=100" width="100px;" alt="wunder957"/><br /><sub><b>wunder957</b></sub></a><br /><a href="#code-wunder957" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/WYXsb"><img src="https://avatars.githubusercontent.com/u/62527555?v=4?s=100" width="100px;" alt="MayDown"/><br /><sub><b>MayDown</b></sub></a><br /><a href="#code-WYXsb" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## How to contribute

Starting with the [good first issue](https://github.com/hitsz-ids/duetector/issues/70) and reading our [contributing guidelines](./CONTRIBUTING.md).

Learn about the designing and architecture of this project here: [docs/design](./docs/design/README.md).

## License

This project uses Apache-2.0 license, please refer to [LICENSE](./LICENSE).
