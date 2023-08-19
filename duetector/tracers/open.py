from collections import namedtuple
from typing import Callable, NamedTuple

from duetector.extension.tracer import hookimpl
from duetector.tracers.base import BccTracer


class OpenTracer(BccTracer):
    attach_type = "kprobe"
    attatch_args = {"fn_name": "trace_entry", "event": "do_sys_openat2"}
    poll_fn = "ring_buffer_poll"
    poll_args = {}
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
        u64 timestamp = bpf_ktime_get_ns();
        bpf_get_current_comm(&data.comm, sizeof(data.comm));
        bpf_probe_read_user_str(&data.fname, sizeof(data.fname), filename);
        buffer.ringbuf_output(&data, sizeof(data), 0);
        return 0;
    }
    """

    def add_callback(self, bpf, callback: Callable[[NamedTuple], None]):
        def _(ctx, data, size):
            event = bpf["buffer"].event(data)
            return callback(self._convert_data(event))  # type: ignore

        bpf["buffer"].open_ring_buffer(_)


@hookimpl
def init_tracer(config):
    return OpenTracer(config)


if __name__ == "__main__":
    from bcc import BPF

    b = BPF(text=OpenTracer.prog)
    tracer = OpenTracer()
    tracer.attach(b)

    def print_callback(data: tracer.data_t):
        print(f"[{data.comm} ({data.pid})] OPEN {data.fname}")

    tracer.add_callback(b, print_callback)
    poller = tracer.get_poller(b)
    while True:
        try:
            poller()
        except KeyboardInterrupt:
            exit()
