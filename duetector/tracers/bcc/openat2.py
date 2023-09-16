from collections import namedtuple
from typing import Callable, NamedTuple

from duetector.extension.tracer import hookimpl
from duetector.tracers.base import BccTracer


class OpenTracer(BccTracer):
    """
    A tracer for openat2 syscall.
    """

    default_config = {
        **BccTracer.default_config,
        "attach_event": "do_sys_openat2",
        "poll_timeout": 10,
    }

    attach_type = "kprobe"

    @property
    def attatch_args(self):
        return {"fn_name": "do_trace", "event": self.config.attach_event}

    attatch_args = {"fn_name": "trace_entry", "event": "do_sys_openat2"}
    poll_fn = "ring_buffer_poll"

    @property
    def poll_args(self):
        return {"timeout": int(self.config.poll_timeout)}

    data_t = namedtuple("OpenTracking", ["pid", "uid", "gid", "comm", "fname", "timestamp"])

    prog = """
    #include <linux/sched.h>
    #include <linux/fs_struct.h>

    struct data_t {
        u32 pid;
        u32 uid;
        u32 gid;
        char comm[TASK_COMM_LEN];
        char fname[NAME_MAX];

        u64 timestamp;
    };

    BPF_RINGBUF_OUTPUT(buffer, 1 << 4);

    int trace_entry(struct pt_regs *ctx, int dfd, const char __user *filename, struct open_how *how) {
        struct data_t data = {};
        data.pid = bpf_get_current_pid_tgid();
        data.uid = bpf_get_current_uid_gid();
        data.gid = bpf_get_current_uid_gid() >> 32;
        data.timestamp = bpf_ktime_get_ns();
        bpf_get_current_comm(&data.comm, sizeof(data.comm));
        bpf_probe_read_user_str(&data.fname, sizeof(data.fname), filename);
        buffer.ringbuf_output(&data, sizeof(data), 0);
        return 0;
    }
    """

    def set_callback(self, host, callback: Callable[[NamedTuple], None]):
        def _(ctx, data, size):
            event = host["buffer"].event(data)
            return callback(self._convert_data(event))  # type: ignore

        host["buffer"].open_ring_buffer(_)


@hookimpl
def init_tracer(config):
    return OpenTracer(config)


if __name__ == "__main__":
    from bcc import BPF

    b = BPF(text=OpenTracer.prog)
    tracer = OpenTracer()
    tracer.attach(b)

    def print_callback(data: NamedTuple):
        print(f"[{data.comm} ({data.pid})] {data.timestamp} OPEN {data.fname}")  # type: ignore

    tracer.set_callback(b, print_callback)
    poller = tracer.get_poller(b)
    while True:
        try:
            poller(**tracer.poll_args)
        except KeyboardInterrupt:
            exit()
