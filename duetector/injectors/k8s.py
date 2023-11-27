from duetector.extension.injector import hookimpl
from duetector.injectors.base import Injector


class K8SInjector(Injector):
    pass


@hookimpl
def init_injector(config=None):
    return K8SInjector(config=config)
