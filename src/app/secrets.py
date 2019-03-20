import os

class Secrets(object):

    def __init__(self):
        pass

    def get(self, path):
        return os.environ[path]

