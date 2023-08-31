Currently we use kprobes, uprobes, Tracepoints, Network releatd BPF features. Please refre to [Kernel Configuration for BPF Features](https://github.com/iovisor/bcc/blob/master/docs/kernel_config.md).

If there is any trouble, [raise an Issue](https://github.com/hitsz-ids/duetector/issues/new).

Known Issues:

<5.8 not support `BPF_RINGBUF_OUTPUT`, we suggest to use 5.8+(5.15+) kernel.

Tested on:

- 5.15.x
- 6.1.x
- 6.4.x
