class TracerError(Exception):
    pass


class TreacerDisabledError(TracerError):
    pass


class ConfigError(Exception):
    pass


class ConfigFileNotFoundError(ConfigError):
    pass
