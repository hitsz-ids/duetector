import pluggy

from .var import project_name

hookimpl = pluggy.HookimplMarker(project_name)
