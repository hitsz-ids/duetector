# Run with docker

> https://hub.docker.com/r/dataucon/duetector/

BCC relies on kernel headers, either by turning on the kernel compilation parameter `CONFIG_IKHEADERS=m` or by installing the `kernel-development-package` provided by the distribution.

Docker (`runC`) 's containers are using the same kernel as the host machine, so it is not possible to have kernel headers built-in in Docker images, since the host machines may not be the same. So The host need to meet one of the above conditions.

There are two options:

1. check to see if there is a `/sys/kernel/kheaders.tar.xz` file, and if there is, mount it directly into the same location as the container

```Bash
docker run -it --rm --privileged \
-v /sys/kernel/kheaders.tar.xz:/sys/kernel/kheaders.tar.xz \
-v /sys/kernel/debug:/sys/kernel/debug \
dataucon/duetector
```

2. If there is no such file, you need to install headers and mount `/usr/lib/modules` into the container, `/usr/lib/modules` is the directory where kernel modules are installed, and `/lib` -> `/usr/lib` is the directory where kernel modules are installed, and usually `/lib` -> `/usr/lib` is the directory where kernel modules are installed. The steps are as follows:
   1. In WSL2, [you need to compile and install headers by yourself](https://github.com/iovisor/bcc/blob/master/INSTALL.md#install-packages), or [directly replace your own compiled kernel](https:// zhuanlan.zhihu.com/p/324530180)
   2. Debian/Ubuntu `sudo apt-get install linux-headers-$(uname -r)`
   3. arch `sudo pacman -S linux-headers`
   4. For other distributions, see https://github.com/iovisor/bcc/blob/master/INSTALL.md

```Bash
docker run -it --rm --privileged \
-v /usr/lib/modules:/usr/lib/modules \
-v /sys/kernel/debug:/sys/kernel/debug \
dataucon/duetector
```
