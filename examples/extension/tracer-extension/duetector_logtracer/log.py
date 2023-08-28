from collections import namedtuple
from typing import Callable, NamedTuple

from duetector.extension.tracer import hookimpl
from duetector.tracers.base import BccTracer


class LogTracer(BccTracer):
    default_config = {
        **BccTracer.default_config,  # inherit default_config
    }

    attach_type = "kprobe"
    attatch_args = {"fn_name": "hello", "event": "__x64_sys_clone"}
    poll_fn = None
    poll_args = {}
    data_t = namedtuple("FieldTracking", ["pid", "uid", "gid", "comm", "fname", "timestamp"])

    prog = """
    int hello(void *ctx) {
        bpf_trace_printk("Hello, World!\\n");
        return 0;
    }
    """

    def set_callback(self, host, callback: Callable[[NamedTuple], None]):
        # No need to collect data
        return


@hookimpl
def init_tracer(config):
    return LogTracer(config)


if __name__ == "__main__":
    from bcc import BPF
    from bcc.utils import printb

    b = BPF(text=LogTracer.prog)
    tracer = LogTracer()
    tracer.attach(b)

    while 1:
        try:
            (task, pid, cpu, flags, ts, msg) = b.trace_fields()
        except ValueError:
            continue
        except KeyboardInterrupt:
            exit()
        printb(b"%-18.9f %-16s %-6d %s" % (ts, task, pid, msg))
