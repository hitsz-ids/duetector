from collections import namedtuple
from typing import Callable, NamedTuple

from duetector.extension.tracer import hookimpl
from duetector.tracers.base import BccTracer
from duetector.utils import inet_ntoa


class TcpconnectTracer(BccTracer):
    """
    A tracer for tcpconnect syscall
    """

    default_config = {
        **BccTracer.default_config,
        "poll_timeout": 10,
    }

    many_attatchs = [
        ("kprobe", {"fn_name": "do_trace", "event": "tcp_v4_connect"}),
        ("kretprobe", {"fn_name": "do_return", "event": "tcp_v4_connect"}),
    ]

    poll_fn = "ring_buffer_poll"

    @property
    def poll_args(self):
        return {"timeout": int(self.config.poll_timeout)}

    data_t = namedtuple(
        "TcpTracking",
        ["pid", "uid", "gid", "comm", "saddr", "daddr", "dport", "timestamp"],
    )

    prog = """
    #include <uapi/linux/ptrace.h>
    #include <net/sock.h>
    #include <bcc/proto.h>
    #define TASK_COMM_LEN 16

    BPF_RINGBUF_OUTPUT(buffer, 1 << 4);
    BPF_HASH(currsock, u32, struct sock *);

    struct event {
        u32 dport;
        u32 saddr;
        u32 daddr;
        u32 pid;
        u32 uid;
        u32 gid;

        u64 timestamp;
        char comm[TASK_COMM_LEN];
    };
    int do_trace(struct pt_regs *ctx, struct sock *sk)
    {
	    u32 pid = bpf_get_current_pid_tgid();

	    // stash the sock ptr for lookup on return
	    currsock.update(&pid, &sk);

	    return 0;
    }

    int do_return(struct pt_regs *ctx)
    {
	    int ret = PT_REGS_RC(ctx);
	    u32 pid = bpf_get_current_pid_tgid();

        struct event event= {};

	    struct sock **skpp;
	    skpp = currsock.lookup(&pid);
	    if (skpp == 0) {
		    return 0;	// missed entry
	    }

	    if (ret != 0) {
		    // failed to send SYNC packet, may not have populated
		    // socket __sk_common.{skc_rcv_saddr, ...}
		    currsock.delete(&pid);
		    return 0;
	    }

	    // pull in details
	    struct sock *skp = *skpp;
	    u32 saddr = skp->__sk_common.skc_rcv_saddr;
	    u32 daddr = skp->__sk_common.skc_daddr;
	    u16 dport = skp->__sk_common.skc_dport;
        event.saddr = saddr;
        event.daddr = daddr;
        event.dport = dport;
        event.pid = pid;
        event.uid = bpf_get_current_uid_gid();
        event.gid = bpf_get_current_uid_gid() >> 32;
        event.timestamp = bpf_ktime_get_ns();
        bpf_get_current_comm(&event.comm, sizeof(event.comm));
	    // output
	    buffer.ringbuf_output(&event, sizeof(event), 0);
	    //bpf_trace_printk("trace_tcp4connect %x %x %d\\n", saddr, daddr, ntohs(dport));

	    currsock.delete(&pid);

	    return 0;
    }
    """

    def _convert_data(self, data) -> NamedTuple:
        data = super()._convert_data(data)
        return data._replace(
            saddr=inet_ntoa(data.saddr).decode("utf-8"),
            daddr=inet_ntoa(data.daddr).decode("utf-8"),
        )  # type: ignore

    def set_callback(self, host, callback: Callable[[NamedTuple], None]):
        def _(ctx, data, size):
            event = host["buffer"].event(data)
            return callback(self._convert_data(event))  # type: ignore

        host["buffer"].open_ring_buffer(_)


@hookimpl
def init_tracer(config):
    return TcpconnectTracer(config)


if __name__ == "__main__":
    from bcc import BPF

    b = BPF(text=TcpconnectTracer.prog)
    tracer = TcpconnectTracer()
    tracer.attach(b)

    def print_callback(data: NamedTuple):
        print(f"[{data.comm} ({data.pid}) {data.uid} {data.gid}] TCP_CONNECT SADDR:{data.saddr} DADDR: {data.daddr} DPORT:{data.dport}")  # type: ignore

    tracer.set_callback(b, print_callback)
    poller = tracer.get_poller(b)
    while True:
        try:
            poller(**tracer.poll_args)
        except KeyboardInterrupt:
            exit()
