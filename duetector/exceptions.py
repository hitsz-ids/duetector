class TracerError(Exception):
    pass


class ConfigError(Exception):
    pass


class ConfigFileNotFoundError(ConfigError):
    pass
