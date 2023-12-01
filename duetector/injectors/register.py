# Expose for plugin system
from . import docker, k8s

registers = [docker, k8s]
