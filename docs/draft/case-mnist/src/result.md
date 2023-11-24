### 画图

- 每个函数一个大模块

- 体现出大体的逻辑

  - 每一个小模块解释系统调用的各个参数情况，之后类似的可以直接代过
  - 对于`mmap`,`brk`用于申请内存的情况，或者`futex`等无关数据部分的调用做下简短说明就好

______________________________________________________________________

### 输出部分

<span style="color:darkorange">需要注意下面仅仅做了划分，可能有些模块开头部分的参数要到上面去找</span>

#### 1. train_data

> ```python
> # 下载mnist手写数据集
> train_data = torchvision.datasets.MNIST(
>     root='./data/',  # 保存或提取的位置  会放在当前文件夹中
>     train=True,  # true说明是用于训练的数据，false说明是用于测试的数据
>     transform=torchvision.transforms.ToTensor(),  # 转换PIL.Image or numpy.ndarray
>
>     download=DOWNLOAD_MNIST,  # 已经下载了就不需要下载了
> )
> ```
>
> ```
> 11257 stat("./data/MNIST/processed", 0x7ffc239123c0) = -1 ENOENT (No such file or directory)
> 11257 stat("./data/MNIST/raw/train-images-idx3-ubyte", {st_mode=S_IFREG|0664, st_size=47040016, ...}) = 0
> 11257 stat("./data/MNIST/raw/train-labels-idx1-ubyte", {st_mode=S_IFREG|0664, st_size=60008, ...}) = 0
> 11257 stat("./data/MNIST/raw/t10k-images-idx3-ubyte", {st_mode=S_IFREG|0664, st_size=7840016, ...}) = 0
> 11257 stat("./data/MNIST/raw/t10k-labels-idx1-ubyte", {st_mode=S_IFREG|0664, st_size=10008, ...}) = 0
> 11257 stat("./data/MNIST/raw/train-images-idx3-ubyte", {st_mode=S_IFREG|0664, st_size=47040016, ...}) = 0
> 11257 stat("./data/MNIST/raw/train-labels-idx1-ubyte", {st_mode=S_IFREG|0664, st_size=60008, ...}) = 0
> 11257 stat("./data/MNIST/raw/t10k-images-idx3-ubyte", {st_mode=S_IFREG|0664, st_size=7840016, ...}) = 0
> 11257 stat("./data/MNIST/raw/t10k-labels-idx1-ubyte", {st_mode=S_IFREG|0664, st_size=10008, ...}) = 0
> 11257 openat(AT_FDCWD, "./data/MNIST/raw/train-images-idx3-ubyte", O_RDONLY|O_CLOEXEC) = 4
> 11257 fstat(4, {st_mode=S_IFREG|0664, st_size=47040016, ...}) = 0
> 11257 ioctl(4, TCGETS, 0x7ffc239120c0)  = -1 ENOTTY (Inappropriate ioctl for device)
> 11257 lseek(4, 0, SEEK_CUR)             = 0
> 11257 lseek(4, 0, SEEK_CUR)             = 0
> 11257 fstat(4, {st_mode=S_IFREG|0664, st_size=47040016, ...}) = 0
> 11257 mmap(NULL, 47042560, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa0ed23000
> 11257 read(4, "\0\0\10\3\0\0\352`\0\0\0\34\0\0\0\34\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 47040017) = 47040016
> 11257 read(4, "", 1)                    = 0
> 11257 close(4)                          = 0
> 11257 stat("/home/tsdsnk/Downloads/home/tsdsnk/software/envs/python39/lib/python3.9/encodings", {st_mode=S_IFDIR|0775, st_size=4096, ...}) = 0
> 11257 stat("/home/tsdsnk/Downloads/home/tsdsnk/software/envs/python39/lib/python3.9/encodings/hex_codec.py", {st_mode=S_IFREG|0664, st_size=1508, ...}) = 0
> 11257 stat("/home/tsdsnk/Downloads/home/tsdsnk/software/envs/python39/lib/python3.9/encodings/hex_codec.py", {st_mode=S_IFREG|0664, st_size=1508, ...}) = 0
> 11257 openat(AT_FDCWD, "/home/tsdsnk/Downloads/home/tsdsnk/software/envs/python39/lib/python3.9/encodings/__pycache__/hex_codec.cpython-39.pyc", O_RDONLY|O_CLOEXEC) = 4
> 11257 fstat(4, {st_mode=S_IFREG|0664, st_size=2350, ...}) = 0
> 11257 ioctl(4, TCGETS, 0x7ffc23910db0)  = -1 ENOTTY (Inappropriate ioctl for device)
> 11257 lseek(4, 0, SEEK_CUR)             = 0
> 11257 lseek(4, 0, SEEK_CUR)             = 0
> 11257 fstat(4, {st_mode=S_IFREG|0664, st_size=2350, ...}) = 0
> 11257 read(4, "a\r\r\n\0\0\0\0\326=\261_\344\5\0\0\343\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 2351) = 2350
> 11257 read(4, "", 1)                    = 0
> 11257 close(4)                          = 0
> 11257 mmap(NULL, 47042560, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa0c046000
> 11257 munmap(0x7ffa0ed23000, 47042560)  = 0
> 11257 openat(AT_FDCWD, "./data/MNIST/raw/train-labels-idx1-ubyte", O_RDONLY|O_CLOEXEC) = 4
> 11257 fstat(4, {st_mode=S_IFREG|0664, st_size=60008, ...}) = 0
> 11257 ioctl(4, TCGETS, 0x7ffc239120c0)  = -1 ENOTTY (Inappropriate ioctl for device)
> 11257 lseek(4, 0, SEEK_CUR)             = 0
> 11257 lseek(4, 0, SEEK_CUR)             = 0
> 11257 fstat(4, {st_mode=S_IFREG|0664, st_size=60008, ...}) = 0
> 11257 read(4, "\0\0\10\1\0\0\352`\5\0\4\1\t\2\1\3\1\4\3\5\3\6\1\7\2\10\6\t\4\0\t\1"..., 60009) = 60008
> 11257 read(4, "", 1)                    = 0
> 11257 close(4)                          = 0
> 11257 brk(0x55809083f000)               = 0x55809083f000
> 11257 brk(0x5580908b4000)               = 0x5580908b4000
> 11257 openat(AT_FDCWD, "/sys/devices/system/cpu/kernel_max", O_RDONLY) = 4
> 11257 read(4, "8191\n", 32)             = 5
> 11257 read(4, "", 27)                   = 0
> 11257 close(4)                          = 0
> 11257 openat(AT_FDCWD, "/sys/devices/system/cpu/possible", O_RDONLY) = 4
> 11257 read(4, "0-127\n", 256)           = 6
> 11257 read(4, "", 250)                  = 0
> 11257 close(4)                          = 0
> 11257 openat(AT_FDCWD, "/sys/devices/system/cpu/present", O_RDONLY) = 4
> 11257 read(4, "0-1\n", 256)             = 4
> 11257 read(4, "", 252)                  = 0
> 11257 close(4)                          = 0
> 11257 openat(AT_FDCWD, "/sys/devices/system/cpu/possible", O_RDONLY) = 4
> 11257 read(4, "0-127\n", 256)           = 6
> 11257 read(4, "", 250)                  = 0
> 11257 close(4)                          = 0
> 11257 openat(AT_FDCWD, "/sys/devices/system/cpu/present", O_RDONLY) = 4
> 11257 read(4, "0-1\n", 256)             = 4
> 11257 read(4, "", 252)                  = 0
> 11257 close(4)                          = 0
> 11257 openat(AT_FDCWD, "/proc/cpuinfo", O_RDONLY) = 4
> 11257 read(4, "processor\t: 0\nvendor_id\t: Genuin"..., 2048) = 2048
> 11257 read(4, "_store_bypass l1tf mds swapgs sr"..., 2001) = 192
> 11257 read(4, "", 2048)                 = 0
> 11257 close(4)                          = 0
> 11257 futex(0x7ffa2d4b3568, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 rt_sigaction(SIGRT_1, {sa_handler=0x7ffa35e91870, sa_mask=[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x7ffa35e42520}, NULL, 8) = 0
> 11257 rt_sigprocmask(SIG_UNBLOCK, [RTMIN RT_1], NULL, 8) = 0
> 11257 mmap(NULL, 8392704, PROT_NONE, MAP_PRIVATE|MAP_ANONYMOUS|MAP_STACK, -1, 0) = 0x7ffa111ff000
> 11257 mprotect(0x7ffa11200000, 8388608, PROT_READ|PROT_WRITE) = 0
> 11257 rt_sigprocmask(SIG_BLOCK, ~[], [], 8) = 0
> 11257 clone3({flags=CLONE_VM|CLONE_FS|CLONE_FILES|CLONE_SIGHAND|CLONE_THREAD|CLONE_SYSVSEM|CLONE_SETTLS|CLONE_PARENT_SETTID|CLONE_CHILD_CLEARTID, child_tid=0x7ffa119ff910, parent_tid=0x7ffa119ff910, exit_signal=0, stack=0x7ffa111ff000, stack_size=0x7fff00, tls=0x7ffa119ff640} => {parent_tid=[11293]}, 88) = 11293
> 11257 rt_sigprocmask(SIG_SETMASK, [], NULL, 8) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAIT_PRIVATE, 0, NULL <unfinished ...>
> 11293 rseq(0x7ffa119fffe0, 0x20, 0, 0x53053053) = 0
> 11293 set_robust_list(0x7ffa119ff920, 24) = 0
> 11293 rt_sigprocmask(SIG_SETMASK, [], NULL, 8) = 0
> 11293 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647 <unfinished ...>
> 11257 <... futex resumed>)              = 0
> 11293 <... futex resumed>)              = 1
> 11257 futex(0x5580907ffdb4, FUTEX_WAIT_PRIVATE, 0, NULL <unfinished ...>
> 11293 mmap(NULL, 134217728, PROT_NONE, MAP_PRIVATE|MAP_ANONYMOUS|MAP_NORESERVE, -1, 0) = 0x7ffa04046000
> 11293 munmap(0x7ffa04046000, 66822144)  = 0
> 11293 munmap(0x7ffa0c000000, 286720)    = 0
> 11293 mprotect(0x7ffa08000000, 135168, PROT_READ|PROT_WRITE) = 0
> 11293 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647 <unfinished ...>
> 11257 <... futex resumed>)              = 0
> 11293 <... futex resumed>)              = 1
> ```

#### 2. test_data

> ```python
> test_data = torchvision.datasets.MNIST(
>    root='./data/',
>    train=False  # 表明是测试集
> )
> ```
>
> ```
> 11257 socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_IP) = 4
> 11257 stat("./data/MNIST/processed", 0x7ffc239123c0) = -1 ENOENT (No such file or directory)
> 11257 stat("./data/MNIST/raw/train-images-idx3-ubyte", {st_mode=S_IFREG|0664, st_size=47040016, ...}) = 0
> 11257 stat("./data/MNIST/raw/train-labels-idx1-ubyte", {st_mode=S_IFREG|0664, st_size=60008, ...}) = 0
> 11257 stat("./data/MNIST/raw/t10k-images-idx3-ubyte", {st_mode=S_IFREG|0664, st_size=7840016, ...}) = 0
> 11257 stat("./data/MNIST/raw/t10k-labels-idx1-ubyte", {st_mode=S_IFREG|0664, st_size=10008, ...}) = 0
> 11257 openat(AT_FDCWD, "./data/MNIST/raw/t10k-images-idx3-ubyte", O_RDONLY|O_CLOEXEC) = 5
> 11257 fstat(5, {st_mode=S_IFREG|0664, st_size=7840016, ...}) = 0
> 11257 ioctl(5, TCGETS, 0x7ffc239120c0)  = -1 ENOTTY (Inappropriate ioctl for device)
> 11257 lseek(5, 0, SEEK_CUR)             = 0
> 11257 lseek(5, 0, SEEK_CUR)             = 0
> 11257 fstat(5, {st_mode=S_IFREG|0664, st_size=7840016, ...}) = 0
> 11257 mmap(NULL, 7843840, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa10a84000
> 11257 read(5,  <unfinished ...>
> 11293 futex(0x5580904cd034, FUTEX_WAIT_PRIVATE, 8, NULL <unfinished ...>
> 11257 <... read resumed>"\0\0\10\3\0\0'\20\0\0\0\34\0\0\0\34\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 7840017) = 7840016
> 11257 read(5, "", 1)                    = 0
> 11257 close(5)                          = 0
> 11257 mmap(NULL, 7843840, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa10309000
> 11257 munmap(0x7ffa10a84000, 7843840)   = 0
> 11257 openat(AT_FDCWD, "./data/MNIST/raw/t10k-labels-idx1-ubyte", O_RDONLY|O_CLOEXEC) = 5
> 11257 fstat(5, {st_mode=S_IFREG|0664, st_size=10008, ...}) = 0
> 11257 ioctl(5, TCGETS, 0x7ffc239120c0)  = -1 ENOTTY (Inappropriate ioctl for device)
> 11257 lseek(5, 0, SEEK_CUR)             = 0
> 11257 lseek(5, 0, SEEK_CUR)             = 0
> 11257 fstat(5, {st_mode=S_IFREG|0664, st_size=10008, ...}) = 0
> 11257 read(5, "\0\0\10\1\0\0'\20\7\2\1\0\4\1\4\t\5\t\0\6\t\0\1\5\t\7\3\4\t\6\6\5"..., 10009) = 10008
> 11257 read(5, "", 1)                    = 0
> 11257 close(5)                          = 0
> ```

#### 3. train_loader

> ```python
> train_loader = Data.DataLoader(
>     dataset=train_data,
>     batch_size=BATCH_SIZE,
>     shuffle=True  # 是否打乱数据，一般都打乱
> )
> ```
>
> ```
> 11257 socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_IP) = 5
> 11257 getsockname(4, {sa_family=AF_INET, sin_port=htons(0), sin_addr=inet_addr("0.0.0.0")}, [16]) = 0
> 11257 getpeername(4, 0x7ffc23912670, [16]) = -1 ENOTCONN (Transport endpoint is not connected)
> 11257 close(4)                          = 0
> ```

#### 4. test_x

> ```python
> test_x = torch.unsqueeze(test_data.train_data, dim=1).type(torch.FloatTensor)[:2000] / 255
>
> ```
>
> ```
> 11257 socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_IP) = 4
> 11257 getsockname(5, {sa_family=AF_INET, sin_port=htons(0), sin_addr=inet_addr("0.0.0.0")}, [16]) = 0
> 11257 getpeername(5, 0x7ffc23912670, [16]) = -1 ENOTCONN (Transport endpoint is not connected)
> 11257 close(5)                          = 0
> 11257 stat("/home/tsdsnk/Downloads/home/tsdsnk/software/envs/python39/lib/python3.9/site-packages/torchvision/datasets/mnist.py", {st_mode=S_IFREG|0664, st_size=21205, ...}) = 0
> 11257 openat(AT_FDCWD, "/home/tsdsnk/Downloads/home/tsdsnk/software/envs/python39/lib/python3.9/site-packages/torchvision/datasets/mnist.py", O_RDONLY|O_CLOEXEC) = 5
> 11257 fstat(5, {st_mode=S_IFREG|0664, st_size=21205, ...}) = 0
> 11257 ioctl(5, TCGETS, 0x7ffc23911670)  = -1 ENOTTY (Inappropriate ioctl for device)
> 11257 lseek(5, 0, SEEK_CUR)             = 0
> 11257 read(5, "import codecs\nimport os\nimport o"..., 4096) = 4096
> 11257 read(5, " label_file = f\"{'train' if self"..., 8192) = 8192
> 11257 read(5, "_label_file(self.labels_file)\n\n "..., 8192) = 8192
> 11257 read(5, "\n    return parsed.view(*s)\n\n\nde"..., 8192) = 725
> 11257 read(5, "", 8192)                 = 0
> 11257 close(5)                          = 0
> 11257 write(2, "/home/tsdsnk/Downloads/home/tsds"..., 218) = 218
> 11257 mmap(NULL, 31363072, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa06217000
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 1
> 11293 <... futex resumed>)              = 0
> 11293 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647 <unfinished ...>
> 11257 brk(0x558090eaf000)               = 0x558090eaf000
> 11257 futex(0x5580904cd034, FUTEX_WAIT_PRIVATE, 16, NULL <unfinished ...>
> 11293 <... futex resumed>)              = 0
> 11293 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 1
> 11257 <... futex resumed>)              = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAIT_PRIVATE, 16, NULL <unfinished ...>
> 11293 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647 <unfinished ...>
> 11257 <... futex resumed>)              = -1 EAGAIN (Resource temporarily unavailable)
> 11293 <... futex resumed>)              = 0
> 11257 munmap(0x7ffa06217000, 31363072 <unfinished ...>
> 11293 futex(0x5580904cd034, FUTEX_WAIT_PRIVATE, 24, NULL <unfinished ...>
> 11257 <... munmap resumed>)             = 0
> ```

#### 5. test_y

> ```python
> test_y = test_data.test_labels[:2000]
> ```
>
> ```
> 11257 socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_IP) = 5
> 11257 getsockname(4, {sa_family=AF_INET, sin_port=htons(0), sin_addr=inet_addr("0.0.0.0")}, [16]) = 0
> 11257 getpeername(4, 0x7ffc23912670, [16]) = -1 ENOTCONN (Transport endpoint is not connected)
> 11257 close(4)                          = 0
> 11257 write(2, "/home/tsdsnk/Downloads/home/tsds"..., 226) = 226
> ```

#### 6. cnn

> ```python
> cnn = CNN()
> ```
>
> ```
> 11257 socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_IP) = 4
> 11257 getsockname(5, {sa_family=AF_INET, sin_port=htons(0), sin_addr=inet_addr("0.0.0.0")}, [16]) = 0
> 11257 getpeername(5, 0x7ffc23912670, [16]) = -1 ENOTCONN (Transport endpoint is not connected)
> 11257 close(5)                          = 0
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa12580000
> ```

#### 7. optimizer

> ```python
> optimizer = torch.optim.Adam(cnn.parameters(), lr=LR)
> ```
>
> ```
> 11257 socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_IP) = 5
> 11257 getsockname(4, {sa_family=AF_INET, sin_port=htons(0), sin_addr=inet_addr("0.0.0.0")}, [16]) = 0
> 11257 getpeername(4, 0x7ffc23912670, [16]) = -1 ENOTCONN (Transport endpoint is not connected)
> 11257 close(4)                          = 0
> ```

#### 8. loss_func

> ```python
> loss_func = nn.CrossEntropyLoss()  # 目标标签是one-hotted
> ```
>
> ```
> 11257 socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_IP) = 4
> 11257 getsockname(5, {sa_family=AF_INET, sin_port=htons(0), sin_addr=inet_addr("0.0.0.0")}, [16]) = 0
> 11257 getpeername(5, 0x7ffc23912670, [16]) = -1 ENOTCONN (Transport endpoint is not connected)
> 11257 close(5)                          = 0
> ```

#### 9. batch_x, batch_y

> ```python
> for step, (b_x, b_y) in enumerate(train_loader):
> ```
>
> ```
> 11257 socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_IP) = 5
> 11257 getsockname(4, {sa_family=AF_INET, sin_port=htons(0), sin_addr=inet_addr("0.0.0.0")}, [16]) = 0
> 11257 getpeername(4, 0x7ffc23912670, [16]) = -1 ENOTCONN (Transport endpoint is not connected)
> 11257 close(4)                          = 0
> 11257 brk(0x558090f40000)               = 0x558090f40000
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 1
> 11293 <... futex resumed>)              = 0
> 11293 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 brk(0x558090fb5000)               = 0x558090fb5000
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0 <unfinished ...>
> 11293 futex(0x5580904cd034, FUTEX_WAIT_PRIVATE, 32, NULL <unfinished ...>
> 11257 <... mmap resumed>)               = 0x7ffa12540000
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa11fc0000
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa11f80000
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa11f40000
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa111bf000
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa1117f000
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa1113f000
> ```

#### 10. output

> ```python
> output = cnn(b_x)
> ```
>
> ```
> 11257 socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_IP) = 4
> 11257 getsockname(5, {sa_family=AF_INET, sin_port=htons(0), sin_addr=inet_addr("0.0.0.0")}, [16]) = 0
> 11257 getpeername(5, 0x7ffc23912670, [16]) = -1 ENOTCONN (Transport endpoint is not connected)
> 11257 close(5)                          = 0
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa110ff000
> 11257 mprotect(0x7ffa110ff000, 262144, PROT_READ|PROT_WRITE|PROT_EXEC) = 0
> 11257 openat(AT_FDCWD, "/home/tsdsnk/Downloads/home/tsdsnk/software/envs/python39/lib/python3.9/site-packages/torch/lib/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/home/tsdsnk/Downloads/home/tsdsnk/software/envs/python39/lib/python3.9/site-packages/torch/lib/../../../../libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/home/tsdsnk/Downloads/home/tsdsnk/software/envs/python39/bin/../lib/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 5
> 11257 newfstatat(5, "", {st_mode=S_IFREG|0644, st_size=64319, ...}, AT_EMPTY_PATH) = 0
> 11257 mmap(NULL, 64319, PROT_READ, MAP_PRIVATE, 5, 0) = 0x7ffa156d5000
> 11257 close(5)                          = 0
> 11257 openat(AT_FDCWD, "/lib/x86_64-linux-gnu/glibc-hwcaps/x86-64-v3/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/lib/x86_64-linux-gnu/glibc-hwcaps/x86-64-v3", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/lib/x86_64-linux-gnu/glibc-hwcaps/x86-64-v2/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/lib/x86_64-linux-gnu/glibc-hwcaps/x86-64-v2", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/lib/x86_64-linux-gnu/tls/haswell/x86_64/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/lib/x86_64-linux-gnu/tls/haswell/x86_64", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/lib/x86_64-linux-gnu/tls/haswell/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/lib/x86_64-linux-gnu/tls/haswell", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/lib/x86_64-linux-gnu/tls/x86_64/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/lib/x86_64-linux-gnu/tls/x86_64", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/lib/x86_64-linux-gnu/tls/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/lib/x86_64-linux-gnu/tls", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/lib/x86_64-linux-gnu/haswell/x86_64/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/lib/x86_64-linux-gnu/haswell/x86_64", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/lib/x86_64-linux-gnu/haswell/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/lib/x86_64-linux-gnu/haswell", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/lib/x86_64-linux-gnu/x86_64/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/lib/x86_64-linux-gnu/x86_64", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/lib/x86_64-linux-gnu", {st_mode=S_IFDIR|0755, st_size=77824, ...}, 0) = 0
> 11257 openat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/glibc-hwcaps/x86-64-v3/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/glibc-hwcaps/x86-64-v3", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/glibc-hwcaps/x86-64-v2/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/glibc-hwcaps/x86-64-v2", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/tls/haswell/x86_64/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/tls/haswell/x86_64", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/tls/haswell/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/tls/haswell", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/tls/x86_64/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/tls/x86_64", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/tls/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/tls", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/haswell/x86_64/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/haswell/x86_64", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/haswell/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/haswell", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/x86_64/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/x86_64", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu", {st_mode=S_IFDIR|0755, st_size=77824, ...}, 0) = 0
> 11257 openat(AT_FDCWD, "/lib/glibc-hwcaps/x86-64-v3/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/lib/glibc-hwcaps/x86-64-v3", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/lib/glibc-hwcaps/x86-64-v2/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/lib/glibc-hwcaps/x86-64-v2", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/lib/tls/haswell/x86_64/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/lib/tls/haswell/x86_64", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/lib/tls/haswell/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/lib/tls/haswell", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/lib/tls/x86_64/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/lib/tls/x86_64", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/lib/tls/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/lib/tls", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/lib/haswell/x86_64/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/lib/haswell/x86_64", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/lib/haswell/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/lib/haswell", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/lib/x86_64/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/lib/x86_64", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/lib/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/lib", {st_mode=S_IFDIR|0755, st_size=4096, ...}, 0) = 0
> 11257 openat(AT_FDCWD, "/usr/lib/glibc-hwcaps/x86-64-v3/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/usr/lib/glibc-hwcaps/x86-64-v3", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/usr/lib/glibc-hwcaps/x86-64-v2/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/usr/lib/glibc-hwcaps/x86-64-v2", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/usr/lib/tls/haswell/x86_64/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/usr/lib/tls/haswell/x86_64", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/usr/lib/tls/haswell/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/usr/lib/tls/haswell", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/usr/lib/tls/x86_64/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/usr/lib/tls/x86_64", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/usr/lib/tls/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/usr/lib/tls", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/usr/lib/haswell/x86_64/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/usr/lib/haswell/x86_64", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/usr/lib/haswell/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/usr/lib/haswell", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/usr/lib/x86_64/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/usr/lib/x86_64", 0x7ffc2390dab0, 0) = -1 ENOENT (No such file or directory)
> 11257 openat(AT_FDCWD, "/usr/lib/libJitPI.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> 11257 newfstatat(AT_FDCWD, "/usr/lib", {st_mode=S_IFDIR|0755, st_size=4096, ...}, 0) = 0
> 11257 munmap(0x7ffa156d5000, 64319)     = 0
> 11257 futex(0x558090ef6fe8, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa110bf000
> 11257 mprotect(0x7ffa110bf000, 262144, PROT_READ|PROT_WRITE|PROT_EXEC) = 0
> 11257 futex(0x5580904661d8, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 1
> 11293 <... futex resumed>)              = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 brk(0x55809121a000)               = 0x55809121a000
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 brk(0x55809147e000)               = 0x55809147e000
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa1107f000
> 11257 mprotect(0x7ffa1107f000, 262144, PROT_READ|PROT_WRITE|PROT_EXEC) = 0
> 11257 futex(0x558090ed6868, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 brk(0x5580916e3000)               = 0x5580916e3000
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa1103f000
> 11257 mprotect(0x7ffa1103f000, 262144, PROT_READ|PROT_WRITE|PROT_EXEC) = 0
> 11257 futex(0x558090eac3a8, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa10fff000
> 11257 mprotect(0x7ffa10fff000, 262144, PROT_READ|PROT_WRITE|PROT_EXEC) = 0
> 11257 futex(0x558090eb0e68, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa10fbf000
> 11257 mprotect(0x7ffa10fbf000, 262144, PROT_READ|PROT_WRITE|PROT_EXEC) = 0
> 11257 futex(0x558090eb06c8, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAIT_PRIVATE, 88, NULL <unfinished ...>
> 11293 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647 <unfinished ...>
> 11257 <... futex resumed>)              = 0
> 11293 <... futex resumed>)              = 1
> 11257 brk(0x558091815000)               = 0x558091815000
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa10f7f000
> 11257 mprotect(0x7ffa10f7f000, 262144, PROT_READ|PROT_WRITE|PROT_EXEC) = 0
> 11257 futex(0x5580903c8b48, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647 <unfinished ...>
> 11293 mprotect(0x7ffa08021000, 4132864, PROT_READ|PROT_WRITE <unfinished ...>
> 11257 <... futex resumed>)              = 0
> 11257 brk(0x558091aef000)               = 0x558091aef000
> 11293 <... mprotect resumed>)           = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> ```

#### 11. loss

> ```python
> loss = loss_func(output, b_y)
> ```
>
> ```
> 11257 socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_IP) = 5
> 11257 getsockname(4, {sa_family=AF_INET, sin_port=htons(0), sin_addr=inet_addr("0.0.0.0")}, [16]) = 0
> 11257 getpeername(4, 0x7ffc23912670, [16]) = -1 ENOTCONN (Transport endpoint is not connected)
> 11257 close(4)                          = 0
> ```

#### 12. zero_grad

> ```python
> optimizer.zero_grad()
> ```
>
> ```
> 11257 socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_IP) = 4
> 11257 getsockname(5, {sa_family=AF_INET, sin_port=htons(0), sin_addr=inet_addr("0.0.0.0")}, [16]) = 0
> 11257 getpeername(5, 0x7ffc23912670, [16]) = -1 ENOTCONN (Transport endpoint is not connected)
> 11257 close(5)                          = 0
> ```

#### 13. backward

> ```python
> loss.backward()
> ```
>
> ```
> 11257 socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_IP <unfinished ...>
> 11293 futex(0x5580904cd034, FUTEX_WAIT_PRIVATE, 128, NULL <unfinished ...>
> 11257 <... socket resumed>)             = 5
> 11257 getsockname(4, {sa_family=AF_INET, sin_port=htons(0), sin_addr=inet_addr("0.0.0.0")}, [16]) = 0
> 11257 getpeername(4, 0x7ffc23912670, [16]) = -1 ENOTCONN (Transport endpoint is not connected)
> 11257 close(4)                          = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 1
> 11293 <... futex resumed>)              = 0
> 11293 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11293 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11293 mprotect(0x7ffa08412000, 4624384, PROT_READ|PROT_WRITE) = 0
> 11293 futex(0x5580907ffdb4, FUTEX_WAIT_PRIVATE, 136, NULL <unfinished ...>
> 11257 brk(0x558091f58000)               = 0x558091f58000
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 1
> 11293 <... futex resumed>)              = 0
> 11293 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11293 futex(0x5580907ffdb4, FUTEX_WAIT_PRIVATE, 144, NULL <unfinished ...>
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 1
> 11293 <... futex resumed>)              = 0
> 11257 brk(0x55809208a000 <unfinished ...>
> 11293 futex(0x5580904cd034, FUTEX_WAIT_PRIVATE, 152, NULL <unfinished ...>
> 11257 <... brk resumed>)                = 0x55809208a000
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 1
> 11293 <... futex resumed>)              = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 brk(0x5580921bd000)               = 0x5580921bd000
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 brk(0x5580922ef000)               = 0x5580922ef000
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa10f3f000
> 11257 mprotect(0x7ffa10f3f000, 262144, PROT_READ|PROT_WRITE|PROT_EXEC) = 0
> 11257 futex(0x558090eccca8, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa10eff000
> 11257 mprotect(0x7ffa10eff000, 262144, PROT_READ|PROT_WRITE|PROT_EXEC <unfinished ...>
> 11293 futex(0x5580904cd034, FUTEX_WAIT_PRIVATE, 184, NULL <unfinished ...>
> 11257 <... mprotect resumed>)           = 0
> 11257 futex(0x558090ec2328, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 1
> 11293 <... futex resumed>)              = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa10ebf000
> 11257 mprotect(0x7ffa10ebf000, 262144, PROT_READ|PROT_WRITE|PROT_EXEC) = 0
> 11257 futex(0x558090ec0d08, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa10e7f000
> 11257 mprotect(0x7ffa10e7f000, 262144, PROT_READ|PROT_WRITE|PROT_EXEC) = 0
> 11257 futex(0x5580911d1d88, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAIT_PRIVATE, 200, NULL <unfinished ...>
> 11293 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 <... futex resumed>)              = -1 EAGAIN (Resource temporarily unavailable)
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa10e3f000
> 11257 mprotect(0x7ffa10e3f000, 262144, PROT_READ|PROT_WRITE|PROT_EXEC) = 0
> 11257 futex(0x558090ebd468, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11293 futex(0x5580907ffdb4, FUTEX_WAIT_PRIVATE, 224, NULL <unfinished ...>
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 1
> 11293 <... futex resumed>)              = 0
> 11257 futex(0x55809006fa48, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa10dff000
> 11257 mprotect(0x7ffa10dff000, 262144, PROT_READ|PROT_WRITE|PROT_EXEC) = 0
> 11257 futex(0x558090ebd868, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 brk(0x558092421000)               = 0x558092421000
> 11257 futex(0x5580904cd034, FUTEX_WAIT_PRIVATE, 248, NULL <unfinished ...>
> 11293 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 1
> 11293 futex(0x5580907ffdb4, FUTEX_WAIT_PRIVATE, 248, NULL <unfinished ...>
> 11257 <... futex resumed>)              = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 1
> 11293 <... futex resumed>)              = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 brk(0x558092686000)               = 0x558092686000
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 brk(0x5580928ea000)               = 0x5580928ea000
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa10dbf000
> 11257 mprotect(0x7ffa10dbf000, 262144, PROT_READ|PROT_WRITE|PROT_EXEC) = 0
> 11257 futex(0x558090eb5a08, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa10d7f000
> 11257 mprotect(0x7ffa10d7f000, 262144, PROT_READ|PROT_WRITE|PROT_EXEC) = 0
> 11257 futex(0x558090eb8ac8, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa10d3f000
> 11257 mprotect(0x7ffa10d3f000, 262144, PROT_READ|PROT_WRITE|PROT_EXEC) = 0
> 11257 futex(0x558090ed82a8, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAIT_PRIVATE, 288, NULL <unfinished ...>
> 11293 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 1
> 11257 <... futex resumed>)              = 0
> 11257 futex(0x558090eb7068, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7ffa10cff000
> 11257 mprotect(0x7ffa10cff000, 262144, PROT_READ|PROT_WRITE|PROT_EXEC) = 0
> 11257 futex(0x558090ec68a8, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> ```

#### 14. step

> ```python
> optimizer.step()
> ```
>
> ```
> 11257 socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_IP) = 4
> 11257 getsockname(5, {sa_family=AF_INET, sin_port=htons(0), sin_addr=inet_addr("0.0.0.0")}, [16]) = 0
> 11257 getpeername(5, 0x7ffc23912670, [16]) = -1 ENOTCONN (Transport endpoint is not connected)
> 11257 close(5)                          = 0
> 11293 futex(0x5580904cd034, FUTEX_WAIT_PRIVATE, 312, NULL <unfinished ...>
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 1
> 11293 <... futex resumed>)              = 0
> 11293 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580904cd034, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 futex(0x5580907ffdb4, FUTEX_WAKE_PRIVATE, 2147483647) = 0
> 11257 munmap(0x7ffa111bf000, 262144)    = 0
> 11257 munmap(0x7ffa11f40000, 262144)    = 0
> 11257 munmap(0x7ffa11f80000, 262144)    = 0
> 11257 munmap(0x7ffa11fc0000, 262144)    = 0
> 11257 munmap(0x7ffa12540000, 262144)    = 0
> ```

#### 15. save

> ```python
> torch.save(cnn.state_dict(), 'cnn2.pkl')
> ```
>
> ```
> 11257 socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_IP) = 5
> 11257 getsockname(4, {sa_family=AF_INET, sin_port=htons(0), sin_addr=inet_addr("0.0.0.0")}, [16]) = 0
> 11257 getpeername(4, 0x7ffc23912670, [16]) = -1 ENOTCONN (Transport endpoint is not connected)
> 11257 close(4)                          = 0
> 11257 openat(AT_FDCWD, "cnn2.pkl", O_WRONLY|O_CREAT|O_TRUNC, 0666) = 4
> 11257 writev(4, [{iov_base="PK\3\4\0\0\10\10\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\r\0\25\0cn"..., iov_len=960}, {iov_base="\372\0\321=&\326\266\275F\350\"\275\2364\276=\214\324A\276\241\230\363=M\240,\275aU\316="..., iov_len=1600}], 2) = 2560
> 11257 writev(4, [{iov_base="PK\7\10\330\341Z\302@\6\0\0@\6\0\0PK\3\4\0\0\10\10\0\0\0\0\0\0\0\0"..., iov_len=192}, {iov_base="\21\276\36\275\32(6=Z\266\0\275\267\373\227\274J\230$\275TG?=7\233\v<PZ(="..., iov_len=51200}], 2) = 51392
> 11257 writev(4, [{iov_base="PK\7\10\361\347\22\342\0\310\0\0\0\310\0\0PK\3\4\0\0\10\10\0\0\0\0\0\0\0\0"..., iov_len=256}, {iov_base="\237\3631<\24n\230\274\307\202\247<Rz\201;\212T\306< G\227\274\4{\300<\340@\217<"..., iov_len=62720}], 2) = 62976
> 11257 write(4, "PK\7\01012\302\370\0\365\0\0\0\365\0\0PK\3\4\0\0\10\10\0\0\0\0\0\0\0\0"..., 767 <unfinished ...>
> ```

#### 16. python函数结束后的部分

> ```
>
> 11293 futex(0x5580904cd034, FUTEX_WAIT_PRIVATE, 328, NULL <unfinished ...>
> 11257 <... write resumed>)              = 767
> 11257 close(4)                          = 0
> 11257 rt_sigaction(SIGINT, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=SA_RESTORER, sa_restorer=0x7ffa35e42520}, {sa_handler=0x55808a124690, sa_mask=[], sa_flags=SA_RESTORER, sa_restorer=0x7ffa35e42520}, 8) = 0
> 11257 getsockname(5, {sa_family=AF_INET, sin_port=htons(0), sin_addr=inet_addr("0.0.0.0")}, [16]) = 0
> 11257 getpeername(5, 0x7ffc23912950, [16]) = -1 ENOTCONN (Transport endpoint is not connected)
> 11257 close(5)                          = 0
> 11257 munmap(0x7ffa10309000, 7843840)   = 0
> 11257 munmap(0x7ffa0c046000, 47042560)  = 0
> 11257 munmap(0x7ffa15f70000, 262144)    = 0
> 11257 munmap(0x7ffa15fb0000, 262144)    = 0
> 11257 close(3)                          = 0
> 11257 mprotect(0x7ffa10cff000, 262144, PROT_READ|PROT_WRITE) = 0
> 11257 munmap(0x7ffa10cff000, 262144)    = 0
> 11257 mprotect(0x7ffa10d7f000, 262144, PROT_READ|PROT_WRITE) = 0
> 11257 munmap(0x7ffa10d7f000, 262144)    = 0
> 11257 mprotect(0x7ffa10dbf000, 262144, PROT_READ|PROT_WRITE) = 0
> 11257 munmap(0x7ffa10dbf000, 262144)    = 0
> 11257 mprotect(0x7ffa10e3f000, 262144, PROT_READ|PROT_WRITE) = 0
> 11257 munmap(0x7ffa10e3f000, 262144)    = 0
> 11257 mprotect(0x7ffa1107f000, 262144, PROT_READ|PROT_WRITE) = 0
> 11257 munmap(0x7ffa1107f000, 262144)    = 0
> 11257 mprotect(0x7ffa110bf000, 262144, PROT_READ|PROT_WRITE) = 0
> 11257 munmap(0x7ffa110bf000, 262144)    = 0
> 11257 mprotect(0x7ffa10dff000, 262144, PROT_READ|PROT_WRITE) = 0
> 11257 munmap(0x7ffa10dff000, 262144)    = 0
> 11257 mprotect(0x7ffa10fff000, 262144, PROT_READ|PROT_WRITE) = 0
> 11257 munmap(0x7ffa10fff000, 262144)    = 0
> 11257 mprotect(0x7ffa110ff000, 262144, PROT_READ|PROT_WRITE) = 0
> 11257 munmap(0x7ffa110ff000, 262144)    = 0
> 11257 mprotect(0x7ffa10f3f000, 262144, PROT_READ|PROT_WRITE) = 0
> 11257 munmap(0x7ffa10f3f000, 262144)    = 0
> 11257 mprotect(0x7ffa10d3f000, 262144, PROT_READ|PROT_WRITE) = 0
> 11257 munmap(0x7ffa10d3f000, 262144)    = 0
> 11257 mprotect(0x7ffa10eff000, 262144, PROT_READ|PROT_WRITE) = 0
> 11257 munmap(0x7ffa10eff000, 262144)    = 0
> 11257 mprotect(0x7ffa1103f000, 262144, PROT_READ|PROT_WRITE) = 0
> 11257 munmap(0x7ffa1103f000, 262144)    = 0
> 11257 mprotect(0x7ffa10f7f000, 262144, PROT_READ|PROT_WRITE) = 0
> 11257 munmap(0x7ffa10f7f000, 262144)    = 0
> 11257 mprotect(0x7ffa10fbf000, 262144, PROT_READ|PROT_WRITE) = 0
> 11257 munmap(0x7ffa10fbf000, 262144)    = 0
> 11257 mprotect(0x7ffa10ebf000, 262144, PROT_READ|PROT_WRITE) = 0
> 11257 munmap(0x7ffa10ebf000, 262144)    = 0
> 11257 mprotect(0x7ffa10e7f000, 262144, PROT_READ|PROT_WRITE) = 0
> 11257 munmap(0x7ffa10e7f000, 262144)    = 0
> 11257 clock_gettime(CLOCK_MONOTONIC, {tv_sec=15014, tv_nsec=428568394}) = 0
> 11257 munmap(0x7ffa2e5af000, 331776)    = 0
> 11257 munmap(0x7ffa1f83b000, 331776)    = 0
> 11257 getpid()                          = 11257
> 11257 exit_group(0)                     = ?
> 11293 <... futex resumed>)              = ?
> 11293 +++ exited with 0 +++
> 11257 +++ exited with 0 +++
> ```
