# CO-RE and SubprocessMonitor

Accroding to [#44](https://github.com/hitsz-ids/duetector/issues/44), this is a draft of CO-RE. It is not a complete version. We will update it in the future.

## Introduction of CO-RE

If you already familiar with [CO-RE](https://facebookmicrosites.github.io/bpf/blog/2020/02/19/bpf-portability-and-co-re.html), you can skip this section.

CO-RE, ...

Requirements of CO-RE:

| Feature               | Kernel version | Commit                                                                                             |
| --------------------- | -------------- | -------------------------------------------------------------------------------------------------- |
| BPF Type Format (BTF) | 4.18           | [`69b693f0aefa`](https://github.com/torvalds/linux/commit/69b693f0aefa0ed521e8bd02260523b5ae446ad7) |

> Note:
>
> - If one `SubprocessTracer` not based on `CO-RE``, it will not require the kernel version.

## 1. Protocol

### 1.1 Protocol Definition

### 1.2 Intergation with OpenTelemetry

## 2. Design

### 2.1 Architecture

### 2.2 Buffer

### 2.3 Failure Handling

## 3. Example

### 3.1 Hello World

## 4. Others

### 4.1 Migrate BccTracer to CO-RE
