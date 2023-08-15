from collections import namedtuple

from duetector.tracers.base import Tracer


class OpenTracer(Tracer):
    attach_type = "kprobe"
    attatch_args = {"fn_name": "trace_entry", "event": "do_sys_openat2"}
    poll_fn = "perf_buffer_poll"
    data_t = namedtuple("DataT", ["pid", "comm", "fname"])

    prog = """
    #include <uapi/linux/ptrace.h>
    #include <linux/sched.h>

    struct data_t {
        u32 pid;
        char comm[TASK_COMM_LEN];
        char fname[NAME_MAX];
    };

    BPF_PERF_OUTPUT(events);

    int trace_entry(struct pt_regs *ctx, int dfd, const char __user *filename, struct open_how *how) {
        struct data_t data = {};
        data.pid = bpf_get_current_pid_tgid();
        bpf_get_current_comm(&data.comm, sizeof(data.comm));
        bpf_probe_read_user_str(&data.fname, sizeof(data.fname), filename);
        events.perf_submit(ctx, &data, sizeof(data));
        return 0;
    }
    """


if __name__ == "__main__":
    from bcc import BPF

    b = BPF(text=OpenTracer.prog)

    OpenTracer.attach(b)

    def print_callback(data: OpenTracer.data_t):
        print(f"[{data.comm} ({data.pid})] OPEN {data.fname}")

    OpenTracer.add_callback(b, print_callback)
    poller = OpenTracer.get_poller(b)
    while True:
        try:
            poller()
        except KeyboardInterrupt:
            exit()
