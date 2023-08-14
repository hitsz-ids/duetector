<h2 align="center">duetector🔍: 基于eBPF的数据使用控制探测器</h2>
<p align="center">
<a href="https://github.com/hitsz-ids/duetector/actions"><img alt="Actions Status" src="https://github.com/hitsz-ids/duetector/actions/workflows/python-package.yml/badge.svg"></a>
<a href="https://results.pre-commit.ci/latest/github/hitsz-ids/duetector/main"><img alt="pre-commit.ci status" src="https://results.pre-commit.ci/badge/github/hitsz-ids/duetector/main.svg"></a>
<a href="https://github.com/hitsz-ids/duetector/blob/main/LICENSE"><img alt="LICENSE" src="https://img.shields.io/github/license/hitsz-ids/duetector"></a>
<a href="https://github.com/hitsz-ids/duetector/releases/"><img alt="Releases" src="https://img.shields.io/github/v/release/hitsz-ids/duetector"></a>
<a href="https://github.com/hitsz-ids/duetector/releases/"><img alt="Pre Releases" src="https://img.shields.io/github/v/release/hitsz-ids/duetector?include_prereleases&label=pre-release&logo=github"></a>
<a href="https://github.com/hitsz-ids/duetector"><img alt="Last Commit" src="https://img.shields.io/github/last-commit/hitsz-ids/duetector"></a>
<a href="https://github.com/hitsz-ids/duetector"><img alt="Python version" src="https://img.shields.io/pypi/pyversions/duetector"></a>
</p>

<p align="center">
<a href="./README.md">中文</a> | <a href="./README_en.md">English</a>
</p>

## 简介

> duetector是DataUCON项目中的组件之一，DataUCON项目旨在为数据使用控制提供支持。[了解DataUCON](https://dataucon.idslab.io/)。

duetector🔍是一个基于eBPF的数据使用控制探测器，它可以在Linux内核中对数据使用行为进行探测，从而为数据使用控制提供支持。

<!-- 这里需要补充ABAUC相关文档，然后替换链接 -->

在[ABAUC控制模型](https://github.com/hitsz-ids/dataucon)当中，duetector可作为PIP（Policy Information Point）来获取数据使用行为，从而为PDP（Policy Decision Point）提供数据使用行为的信息。

## 目录

- [主要特性](#主要特性)
- [安装](#安装)
- [快速开始](#快速开始)
- [API文档](#API文档)
- [维护者](#维护者)
- [如何贡献](#如何贡献)
- [许可证](#许可证)

## 主要特性

TBD

TODO: 特性和[对应的内核配置](https://github.com/iovisor/bcc/blob/master/docs/kernel_config.md)

## 安装

代码通过Pypi分发，你可以通过以下命令安装

```bash
pip install duetector
```

目前，代码依赖[BCC](https://github.com/iovisor/bcc)对eBPF代码进行即时编译，推荐[安装最新的BCC编译器](https://github.com/iovisor/bcc/blob/master/INSTALL.md)

或使用我们提供的Docker镜像

```bash
docker pull dataucon/duetector:latest
```

预发布版本将不会更新到 `latest`上，您可以指定tag进行拉取，如 `v0.1.0`

```bash
docker pull dataucon/duetector:v0.1.0
```

## 快速开始

TBD

更多文档和例子可以在[这里](./docs/)找到。

## API文档

TBD

## 维护者

本项目由**哈尔滨工业大学（深圳）数据安全研究院**发起，若您对本项目以及DataUCON项目感兴趣并愿意一起完善它，欢迎加入我们的开源社区。

## 如何贡献

非常欢迎你的加入！[提一个 Issue](https://github.com/hitsz-ids/duetector/issues/new) 或者提交一个 Pull Request。

开发环境配置和其他注意事项请参考[开发者文档](./DEVELOP.md)。

## 许可证

本项目使用 Apache-2.0 license，有关协议请参考[LICENSE](https://github.com/hitsz-ids/duetector/blob/main/LICENSE)。
