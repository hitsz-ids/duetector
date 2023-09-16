from collections import namedtuple
from typing import Callable, NamedTuple

from duetector.extension.tracer import hookimpl
from duetector.tracers.base import BccTracer


class CloneTracer(BccTracer):
    """
    A tracer for clone syscall.
    """

    default_config = {
        **BccTracer.default_config,
        "attach_event": "__x64_sys_clone",
        "poll_timeout": 10,
    }
    attach_type = "kprobe"

    @property
    def attatch_args(self):
        return {"fn_name": "do_trace", "event": self.config.attach_event}

    poll_fn = "perf_buffer_poll"

    @property
    def poll_args(self):
        return {"timeout": int(self.config.poll_timeout)}

    data_t = namedtuple("CloneTracking", ["pid", "timestamp", "comm"])
    prog = """
    #include <linux/sched.h>

    // define output data structure in C
    struct data_t {
        u32 pid;
        u32 uid;
        u32 gid;
        u64 timestamp;
        char comm[TASK_COMM_LEN];
    };
    BPF_PERF_OUTPUT(events);

    int do_trace(struct pt_regs *ctx) {
        struct data_t data = {};

        data.pid = bpf_get_current_pid_tgid();
        data.uid = bpf_get_current_uid_gid();
        data.gid = bpf_get_current_uid_gid() >> 32;
        data.timestamp = bpf_ktime_get_ns();
        bpf_get_current_comm(&data.comm, sizeof(data.comm));

        events.perf_submit(ctx, &data, sizeof(data));

        return 0;
    }
    """

    def set_callback(self, host, callback: Callable[[NamedTuple], None]):
        def _(ctx, data, size):
            event = host["events"].event(data)
            return callback(self._convert_data(event))  # type: ignore

        host["events"].open_perf_buffer(_)


@hookimpl
def init_tracer(config):
    return CloneTracer(config)


if __name__ == "__main__":
    from bcc import BPF

    b = BPF(text=CloneTracer.prog)

    tracer = CloneTracer()
    tracer.attach(b)
    start = 0

    def print_callback(data: NamedTuple):
        global start
        if start == 0:
            print(f"[{data.comm} ({data.pid})] 0 ")
        else:
            print(f"[{data.comm} ({data.pid}) {data.gid} {data.uid}]  {(data.timestamp-start)/1000000000}")  # type: ignore
        start = data.timestamp

    tracer.set_callback(b, print_callback)
    poller = tracer.get_poller(b)
    while True:
        try:
            poller(**tracer.poll_args)
        except KeyboardInterrupt:
            exit()
