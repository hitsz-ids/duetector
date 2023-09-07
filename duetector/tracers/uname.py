from duetector.extension.tracer import hookimpl
from duetector.tracers.base import ShellTracer


class UnameTracer(ShellTracer):
    """
    A tracer for uname command.
    """

    comm = ["uname", "-a"]


@hookimpl
def init_tracer(config):
    return UnameTracer(config)


if __name__ == "__main__":
    import subprocess

    p = subprocess.Popen(UnameTracer.comm, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    print(p.stdout.read().decode("utf-8"))
