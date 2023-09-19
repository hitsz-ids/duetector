# Run with docker

> Get the image from [dockerhub](https://hub.docker.com/r/dataucon/duetector/).

BCC relies on kernel headers, either by turning on the kernel compilation parameter `CONFIG_IKHEADERS=m` or by installing the `kernel-development-package` provided by the distribution.

Docker (`runC`) 's containers are using the same kernel as the host machine, so it is not possible to have kernel headers built-in in Docker images, since the host machines may not be the same. So The host need to meet one of the above conditions.

There are two options:

1. check to see if there is a `/sys/kernel/kheaders.tar.xz` file, and if there is, mount it directly into the same location as the container

```Bash
docker run -it --rm --privileged \
-p 8888:8888 \
-p 8120:8120 \
--entrypoint bash \
-v /sys/kernel/kheaders.tar.xz:/sys/kernel/kheaders.tar.xz \
-v /sys/kernel/debug:/sys/kernel/debug \
dataucon/duetector
```

2. If there is no such file, you need to install headers and mount `/lib/modules` into the container, `/lib/modules` is the directory where kernel modules are installed, and usually `/lib` is a symbol link of `/usr/lib` (which means `/lib` -> `/usr/lib`). First you need to install the headers:
   1. In WSL2, [you need to compile and install headers by yourself](https://github.com/iovisor/bcc/blob/master/INSTALL.md#install-packages), or [directly replace your own compiled kernel](https://learn.microsoft.com/en-us/windows/wsl/wsl-config)
   2. Debian/Ubuntu: `sudo apt-get install linux-headers-$(uname -r)`
   3. Arch Linux: `sudo pacman -S linux-headers`
   4. For other distributions, please refer to [bcc&#39;s install docs](https://github.com/iovisor/bcc/blob/master/INSTALL.md).

Then mount `/lib/modules` into the container:

```Bash
docker run -it --rm --privileged \
-p 8888:8888 \
-p 8120:8120 \
--entrypoint bash \
-v /lib/modules:/lib/modules \
-v /sys/kernel/debug:/sys/kernel/debug \
dataucon/duetector
```

(**Debian/Ubuntu**) Sometimes `/lib/modules/{kernel-version}/build` is a symbol link of `/usr/src/linux-headers-{kernel-version}`, so you need to mount `/usr/src` also.

```Bash
docker run -it --rm --privileged \
-p 8888:8888 \
-p 8120:8120 \
--entrypoint bash \
-v /lib/modules:/lib/modules \
-v /usr/src:/usr/src \
-v /sys/kernel/debug:/sys/kernel/debug \
dataucon/duetector
```
