![](https://img.shields.io/github/license/hitsz-ids/duetector)
![](https://img.shields.io/github/v/release/hitsz-ids/duetector)
![](https://img.shields.io/pypi/dm/duetector)
![](https://img.shields.io/github/last-commit/hitsz-ids/duetector)
![](https://img.shields.io/pypi/pyversions/duetector)
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

[中文](README.md) | [English](README_en.md)

# duetector🔍: 基于eBPF的数据使用控制探测器

## 简介

[了解DataUCON](https://dataucon.idslab.io/)

[深入阅读DataUCON文档](https://github.com/hitsz-ids/dataucon)

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

## API文档

TBD

## 维护者

本项目由**哈尔滨工业大学（深圳）数据安全研究院**发起，若您对本项目以及DataUCON项目感兴趣并愿意一起完善它，欢迎加入我们的开源社区。

## 如何贡献

非常欢迎你的加入！[提一个 Issue](https://github.com/hitsz-ids/duetector/issues/new) 或者提交一个 Pull Request。

开发环境配置和其他注意事项请参考[开发者文档](./DEVELOP.md)。

## 许可证

本项目使用 Apache-2.0 license，有关协议请参考[LICENSE](https://github.com/hitsz-ids/duetector/blob/main/LICENSE)。
