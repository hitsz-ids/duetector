from typing import NamedTuple, Optional


class Filter:
    def __call__(self, data: NamedTuple) -> Optional[NamedTuple]:
        fname = getattr(data, "fname")
        if fname and any(
            [
                fname.startswith(p)
                for p in [
                    "/proc",
                    "/sys",
                    "/lib",
                    "/dev",
                    "/run",
                    "/usr/lib",
                    "/etc/ld.so.cache",
                ]
            ]
        ):
            return None

        return data
