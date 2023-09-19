# Run with Kata Containers

> Get the image from [dockerhub](https://hub.docker.com/r/dataucon/duetector/).

> Kata Containers is a lightweight virtual machine (VM) for containers.
> It is designed to provide the speed of containers and the isolation of VMs.
> Kata Containers can run on multiple hypervisors and is compatible CRI for Kubernetes.

**The documentation is based on Kata Containers 3.1.3, but in practice kata 3.x should be able to follow this documentation.**

The pre-built kernel from Kata Containers does not support eBPF, so we need to build the kernel ourselves. this documentation is about how to [build the kernel and configure kata containers to use it](https://github.com/kata-containers/kata-containers/blob/main/tools/packaging/kernel/README.md).

If you haven't installed Kata Containers yet, please refer to the [official documentation](https://github.com/kata-containers/kata-containers/tree/main/docs/install).

## Get code from github

```bash
git clone --depth 1 --branch 3.1.3 https://github.com/kata-containers/kata-containers.git
```

## Setup the kernel

1. Download the kernel source code, version 6.1.38 as an example

```bash
cd kata-containers/tools/packaging/kernel
./build-kernel.sh -v 6.1.38 setup
```

2. Change `tools/packaging/kernel/configs/fragments/x86_64/.config` to meet [kernel_config requirements](../kernel_config.md), given an full example [here](./etc/kata-linux-6.1.38-100.config)
3. Build the kernel

```bash
./build-kernel.sh -v 6.1.38 build
```

4. Install the kernel to `/usr/share/kata-containers/`

```bash
sudo ./build-kernel.sh install
```

## Configure kata containers

Kata-qemu config file as example: Edit `/opt/kata/share/defaults/kata-containers/configuration-qemu.toml `

```toml
# Replace the kernel path
#kernel = "/opt/kata/share/kata-containers/vmlinux.container"
kernel = "/usr/share/kata-containers/vmlinuz.container"
```

## Verify

Start container via `nerdctl`

```bash
sudo nerdctl run -it --runtime=io.containerd.kata.v2 --rm alpine
```

Run `uname -a`

```
Linux 856b63ebabcc 6.1.38 #2 SMP Fri Aug 11 16:20:36 CST 2023 x86_64 Linux
```

## Run duetector images

```bash
sudo nerdctl run \
-it \
-p 8888:8888 \
-p 8120:8120 \
--runtime=io.containerd.kata.v2 \
--cap-add=sys_admin \
--entrypoint bash \
--rm \
dataucon/duetector
```

If use `bash` as entrypoint, you need to mount debugfs manually

```bash
mount -t debugfs debugfs /sys/kernel/debug
```

More information about tracking mlflow with duetector, please refer to [usercases](../usercases/tracking-mljob-in-kata-containers/README.md)
