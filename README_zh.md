<h2 align="center">duetector🔍: 支持eBPF的可扩展数据使用探测器</h2>
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

## 简介

> duetector是DataUCON项目中的组件之一，DataUCON项目旨在为数据使用控制提供支持。
>
> [查看DataUCON的网页](https://dataucon.idslab.io/)
>
> [深入了解并部署DataUCON](https://github.com/hitsz-ids/dataucon)

duetector🔍是一个基于可扩展的的数据使用探测器，它可以在Linux内核中对数据使用行为进行探测（基于eBPF），从而为数据使用控制提供支持。

**🐛🐞🧪 项目正在大力开发中，期待任何Bug报告、功能请求、合并请求**

在[ABAUC控制模型](https://github.com/hitsz-ids/dataucon)当中，duetector可作为PIP（Policy Information Point）来获取数据使用行为，从而为PDP（Policy Decision Point）提供数据使用行为的信息。[快速了解用户案例](./docs/usercases/)

## 目录

- [主要特性](#主要特性)
- [安装](#安装)
- [快速开始](#快速开始)
- [API文档与配置文档](#API文档与配置文档)
- [维护者](#维护者)
- [如何贡献](#如何贡献)
- [许可证](#许可证)

## 主要特性

- [X] 插件化系统
  - [X] 支持自定义tracer
  - [X] 支持自定义filter
  - [X] 支持自定义collector
  - [X] [自定义插件示例](./examples/)
- [ ] 配置管理
  - [X] 使用单一配置文件配置
  - [X] 支持生成插件配置
  - [ ] 支持动态加载配置
- [ ] 基于eBPF的数据使用探测器
  - [X] 文件打开操作
  - [ ] ……
- [ ] 基于Shell命令的探测器
  - [X] 内核信息探测
  - [ ] ……
- [X] 支持SQL数据库的数据收集器
- [X] CLI工具
- [ ] PIP服务

eBPF程序需要内核支持，详见[内核支持](./docs/kernel_config.md)

## 安装

代码通过Pypi分发，你可以通过以下命令安装

```bash
pip install duetector
```

目前，代码依赖[BCC](https://github.com/iovisor/bcc)对eBPF代码进行即时编译，推荐[安装最新的BCC编译器](https://github.com/iovisor/bcc/blob/master/INSTALL.md)

或使用我们提供的Docker镜像，其使用[JupyterLab](https://github.com/jupyterlab/jupyterlab)作为**示例**用户应用，您也可以自行修改[Dockerfile](./docker/Dockerfile)和[启动脚本](./docker/start.sh)来自定义用户程序

```bash
docker pull dataucon/duetector:latest
```

预发布版本将不会更新到 `latest`上，您可以指定tag进行拉取，如 `v0.0.1a`

```bash
docker pull dataucon/duetector:v0.0.1a
```

使用docker镜像运行的更多细节请参考[这里](./docs/how-to/run-with-docker.md)

## 快速开始

> 更多文档和例子可以在[这里](./docs/)找到。

### 启动探测器

使用命令行启动monitor，由于bcc需要root权限，所以我们使用 `sudo` 命令，这将启动所有的探测器，并将探测内容收集到当前目录下的 `duetector-dbcollector.sqlite3`文件中

```bash
sudo duectl start
```

按下 `CRTL+C`可以退出监测，你将看到屏幕上输出了一段总结

```
{'DBCollector': {'OpenTracer': {'count': 31, 'first at': 249920233249912, 'last': Tracking(tracer='OpenTracer', pid=641616, uid=1000, gid=1000, comm='node', cwd=None, fname='SOME-FILE', timestamp=249923762308577, extended={})}}}
```

启动 `DEBUG`日志

```bash
sudo DUETECTOR_LOG_LEVEL=DEBUG duectl start
```

启动时，配置文件将自动生成，对应路径为 `~/.config/duetector` ，修改这个配置文件可以修改数据库地址等内容，可以使用 `--config`指定使用的配置文件

```bash
sudo duectl start --config <config-file-path>
```

也支持使用环境变量进行配置:

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

当使用插件时，默认的配置文件不会包含插件的配置内容，使用动态生成配置的指令生成带有插件配置的配置文件，这个指令也支持合并当前已有的配置文件和环境变量

```bash
duectl generate-dynamic-config --help
```

当配置文件出错时，可以使用 `generate-config` 恢复默认状态

```bash
duectl generate-config
```

更进一步的，后台运行可以使用 `duectl-daemon start`命令，这将会在后台运行一个守护进程，你可以使用 `duectl-daemon stop`来停止它

使用 `duectl-daemon --help` 获取更多细节：

```bash
Usage: duectl-daemon [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  start   Start a background process of command `duectl start`.
  status  Show status of process.
  stop    Stop the process.
```

### 使用Analyzer进行分析

我们提供了一个[Analyzer](https://duetector.readthedocs.io/en/latest/analyzer/index.html)，它可以对存储中的数据进行查询，在这里我们提供了一个[入门案例](./docs/usercases/simplest-open-count/README.md)

### 使用Duetector Server

我们提供了一个Duetector Server，作为外部PIP服务和控制接口

使用 `duectl-server`可以启动一个Duetector Server，默认将监听 `0.0.0.0:8120`，你可以使用 `--host`和 `--port`来修改它。

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

在服务启动后，访问 `http://{ip}:{port}/docs`可以查看API文档。

同样的，使用 `duectl-server-daemon start`可以在后台运行一个Duetector Server，你可以使用 `duectl-server-daemon stop`来停止它

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

## API文档与配置文档

我们在readthedocs上为开发者和用户提供了API与配置文档，你可以在[这里](https://duetector.readthedocs.io/)查看

## 维护者

本项目由**哈尔滨工业大学（深圳）数据安全研究院**发起，若您对本项目以及DataUCON项目感兴趣并愿意一起完善它，欢迎加入我们的开源社区。

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


## 如何贡献

非常欢迎您的加入！[我们欢迎任何类型的Issue](https://github.com/hitsz-ids/duetector/issues/new)，同时也期待您的PR

我们提供了以下资料让您更快了解项目

- 开发环境配置和其他注意事项请参考：[开发者文档](./CONTRIBUTING.md)
- 在这里了解本项目的设计思路和架构：[设计文档](./docs/design/README.md)

# 如何开发插件

目前，tracer、filter、collector都支持自定义插件开发，以Python包作为单个插件或多个插件，可以查看[自定义插件示例](./examples/)了解开发步骤

TODO: 提供一个插件的cookiecutter模板

## 许可证

本项目使用 Apache-2.0 license，有关协议请参考[LICENSE](https://github.com/hitsz-ids/duetector/blob/main/LICENSE)。
