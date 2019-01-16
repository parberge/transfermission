
class Config(dict):
    """A proxy class for config to be accessible from anywhere"""
    config = {}
    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, key, value):
        self.config[key] = value

    def update(self, *args, **kwargs):
        self.config.update(*args, **kwargs)

config = Config()
