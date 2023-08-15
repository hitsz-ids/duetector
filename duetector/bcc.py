try:
    from bcc import BPF  # noqa

    testing_mode = False  # noqa
except ImportError:
    testing_mode = True  # noqa

    class BPF:
        def __init__():
            pass

        def attach_dummy(self, **kwargs):
            pass
