from duetector.extension.injector import hookimpl
from duetector.injectors.base import Injector


class DockerInjector(Injector):
    pass


@hookimpl
def init_injector(config=None):
    return DockerInjector(config=config)
